/*
 * USB-TMC callbacks for the PMVB Phase 0 stub firmware.
 *
 * Implements the minimal set of USB488 / SCPI behavior that PyVISA-py needs to
 * enumerate the device and round-trip an *IDN? query. The IDN response is
 * built at startup from the Pico 2 W's unique 64-bit chip ID so each flashed
 * board reports a distinct serial in the SCPI dialect AND in the USB
 * iSerialNumber field (handled in usb_descriptors.c).
 *
 * Supported SCPI commands:
 *   *IDN?           -> "PMVB,Pico 2 W,<chip_id_hex>,1.0.0\n"
 *   *RST            -> silent ack
 *   *CLS            -> silent ack (clear status register)
 *   *OPC?           -> "1\n"
 *   :SYST:BOOTSEL   -> reboot the Pico into BOOTSEL (mass-storage) mode
 *                      for hot re-flashing without the physical button
 *
 * Anything else is silently dropped.
 *
 * This is throwaway probe firmware, NOT the eventual per-module SCPI parser.
 * Real per-module firmware ships with each module's own phase and uses the
 * YAML command schema described in SDD §10.1.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pico/bootrom.h"
#include "pico/unique_id.h"
#include "tusb.h"

#define IDN_MAX_LEN   80

/* Built once at startup, then constant for the life of the firmware. */
static char idn_response[IDN_MAX_LEN];
static size_t idn_response_len = 0;

/* Single-shot response buffer for whatever query is in flight. */
static const char *pending_response = NULL;
static size_t pending_response_len = 0;
static size_t pending_tx_ix = 0;
static volatile bool bulk_in_started = false;
static volatile bool reset_to_bootsel = false;

/* ---------- USB-TMC capabilities advertised to the host ---------- */

static usbtmc_response_capabilities_488_t const pmvb_usbtmc_capabilities = {
    .USBTMC_status = USBTMC_STATUS_SUCCESS,
    .bcdUSBTMC = USBTMC_VERSION,
    .bmIntfcCapabilities = {
        .listenOnly = 0,
        .talkOnly = 0,
        .supportsIndicatorPulse = 0,
    },
    .bmDevCapabilities = {
        .canEndBulkInOnTermChar = 0,
    },
    .bcdUSB488 = USBTMC_488_VERSION,
    .bmIntfcCapabilities488 = {
        .supportsTrigger = 0,
        .supportsREN_GTL_LLO = 0,
        .is488_2 = 1,
    },
    .bmDevCapabilities488 = {
        .SCPI = 1,
        .SR1 = 0,
        .RL1 = 0,
        .DT1 = 0,
    },
};

usbtmc_response_capabilities_488_t const *tud_usbtmc_get_capabilities_cb(void) {
    return &pmvb_usbtmc_capabilities;
}

/* ---------- Setup: build the IDN response from the chip ID ---------- */

void pmvb_usbtmc_init(void) {
    pico_unique_board_id_t board_id;
    pico_get_unique_board_id(&board_id);

    char serial_hex[17];
    for (int i = 0; i < 8; i++) {
        snprintf(&serial_hex[i * 2], 3, "%02X", board_id.id[i]);
    }
    serial_hex[16] = '\0';

    idn_response_len = (size_t) snprintf(idn_response, sizeof(idn_response),
        "PMVB,Pico 2 W,%s,1.0.0\n", serial_hex);
}

/* ---------- SCPI command dispatch ---------- */

/* Case-insensitive prefix match. Returns true if `data` starts with `prefix`. */
static bool starts_with_ci(const char *data, size_t data_len, const char *prefix) {
    size_t plen = strlen(prefix);
    if (data_len < plen) return false;
    for (size_t i = 0; i < plen; i++) {
        char a = data[i];
        char b = prefix[i];
        if (a >= 'a' && a <= 'z') a = (char) (a - 'a' + 'A');
        if (b >= 'a' && b <= 'z') b = (char) (b - 'a' + 'A');
        if (a != b) return false;
    }
    return true;
}

static void handle_scpi(const char *cmd, size_t len) {
    /* Trim trailing whitespace / newline / null */
    while (len > 0 && (cmd[len - 1] == '\n' || cmd[len - 1] == '\r' ||
                       cmd[len - 1] == ' '  || cmd[len - 1] == '\0')) {
        len--;
    }

    pending_response = NULL;
    pending_response_len = 0;
    pending_tx_ix = 0;

    if (starts_with_ci(cmd, len, "*IDN?")) {
        pending_response = idn_response;
        pending_response_len = idn_response_len;
    } else if (starts_with_ci(cmd, len, "*OPC?")) {
        static const char opc_response[] = "1\n";
        pending_response = opc_response;
        pending_response_len = sizeof(opc_response) - 1;
    } else if (starts_with_ci(cmd, len, "*RST") ||
               starts_with_ci(cmd, len, "*CLS")) {
        /* Silent ack */
    } else if (starts_with_ci(cmd, len, ":SYST:BOOTSEL") ||
               starts_with_ci(cmd, len, "SYST:BOOTSEL")) {
        /* PMVB extension: re-enter BOOTSEL on next iteration of main loop
         * so the host can drag-drop a new .uf2 without the physical button. */
        reset_to_bootsel = true;
    }
    /* Unknown commands: silently ignored */
}

/* Polled from main: complete the bootsel reset request out of USB context. */
void pmvb_usbtmc_task_iter(void) {
    if (reset_to_bootsel) {
        /* Give USB a moment to flush before resetting. */
        sleep_ms(50);
        /* Args: usb_activity_gpio_pin_mask=0 (no LED), disable_interface_mask=0
         * (both MSC and PICOBOOT enabled in BOOTSEL). */
        reset_usb_boot(0, 0);
        /* unreachable */
    }
}

/* ---------- TinyUSB USB-TMC class callbacks ---------- */

void tud_usbtmc_open_cb(uint8_t interface_id) {
    (void) interface_id;
    tud_usbtmc_start_bus_read();
}

bool tud_usbtmc_msgBulkOut_start_cb(usbtmc_msg_request_dev_dep_out const *msgHeader) {
    (void) msgHeader;
    return true;
}

bool tud_usbtmc_msg_data_cb(void *data, size_t len, bool transfer_complete) {
    if (transfer_complete) {
        handle_scpi((const char *) data, len);
    }
    tud_usbtmc_start_bus_read();
    return true;
}

bool tud_usbtmc_msgBulkIn_request_cb(usbtmc_msg_request_dev_dep_in const *request) {
    if (pending_response && pending_response_len > 0) {
        size_t remaining = pending_response_len - pending_tx_ix;
        size_t to_send = (remaining < request->TransferSize) ? remaining : request->TransferSize;
        bool eom = (pending_tx_ix + to_send) >= pending_response_len;
        tud_usbtmc_transmit_dev_msg_data(pending_response + pending_tx_ix, to_send, eom, false);
        pending_tx_ix += to_send;
        bulk_in_started = true;
    } else {
        /* No pending response: per USB-TMC spec, NAK rather than stall. */
        bulk_in_started = true;
    }
    return true;
}

bool tud_usbtmc_msgBulkIn_complete_cb(void) {
    if (pending_response && pending_tx_ix >= pending_response_len) {
        pending_response = NULL;
        pending_response_len = 0;
        pending_tx_ix = 0;
    }
    bulk_in_started = false;
    tud_usbtmc_start_bus_read();
    return true;
}

bool tud_usbtmc_msg_trigger_cb(usbtmc_msg_generic_t *msg) {
    (void) msg;
    return true;
}

void tud_usbtmc_bulkOut_clearFeature_cb(void) {
    tud_usbtmc_start_bus_read();
}

void tud_usbtmc_bulkIn_clearFeature_cb(void) {
}

bool tud_usbtmc_initiate_clear_cb(uint8_t *tmcResult) {
    pending_response = NULL;
    pending_response_len = 0;
    pending_tx_ix = 0;
    bulk_in_started = false;
    *tmcResult = USBTMC_STATUS_SUCCESS;
    return true;
}

bool tud_usbtmc_check_clear_cb(usbtmc_get_clear_status_rsp_t *rsp) {
    pending_response = NULL;
    pending_response_len = 0;
    pending_tx_ix = 0;
    bulk_in_started = false;
    rsp->USBTMC_status = USBTMC_STATUS_SUCCESS;
    rsp->bmClear.BulkInFifoBytes = 0u;
    return true;
}

bool tud_usbtmc_initiate_abort_bulk_in_cb(uint8_t *tmcResult) {
    bulk_in_started = false;
    *tmcResult = USBTMC_STATUS_SUCCESS;
    return true;
}

bool tud_usbtmc_check_abort_bulk_in_cb(usbtmc_check_abort_bulk_rsp_t *rsp) {
    (void) rsp;
    tud_usbtmc_start_bus_read();
    return true;
}

bool tud_usbtmc_initiate_abort_bulk_out_cb(uint8_t *tmcResult) {
    *tmcResult = USBTMC_STATUS_SUCCESS;
    return true;
}

bool tud_usbtmc_check_abort_bulk_out_cb(usbtmc_check_abort_bulk_rsp_t *rsp) {
    (void) rsp;
    tud_usbtmc_start_bus_read();
    return true;
}

uint8_t tud_usbtmc_get_stb_cb(uint8_t *tmcResult) {
    *tmcResult = USBTMC_STATUS_SUCCESS;
    /* No status flags ever set in this stub. */
    return 0;
}
