/*
 * USB descriptors for the PMVB USB-TMC stub firmware.
 *
 * One configuration, one USB-TMC interface (USB488 subclass for SCPI compliance),
 * two bulk endpoints + one interrupt-in endpoint. iSerialNumber is populated at
 * runtime from the Pico 2 W's unique 64-bit chip ID via the TinyUSB BSP, giving
 * each flashed Pico a stable USB serial number for the SDD §10.1 hot-plug-by-
 * serial discovery pattern.
 */

#include "bsp/board_api.h"
#include "tusb.h"
#include "class/usbtmc/usbtmc.h"
#include "class/usbtmc/usbtmc_device.h"

/* VID/PID. 0xCafe is the TinyUSB community-reserved test VID; safe for hobby
 * and lab-internal devices but not for any product shipped to the public.
 * 0x4001 is the PMVB-specific PID for this USB-TMC class device. */
#define USB_VID   0xCafe
#define USB_PID   0x4001
#define USB_BCD   0x0200

/* ---------- Device Descriptor ---------- */

tusb_desc_device_t const desc_device = {
    .bLength            = sizeof(tusb_desc_device_t),
    .bDescriptorType    = TUSB_DESC_DEVICE,
    .bcdUSB             = USB_BCD,
    .bDeviceClass       = TUSB_CLASS_UNSPECIFIED,
    .bDeviceSubClass    = 0x00,
    .bDeviceProtocol    = 0x00,
    .bMaxPacketSize0    = CFG_TUD_ENDPOINT0_SIZE,
    .idVendor           = USB_VID,
    .idProduct          = USB_PID,
    .bcdDevice          = 0x0100,
    .iManufacturer      = 0x01,
    .iProduct           = 0x02,
    .iSerialNumber      = 0x03,
    .bNumConfigurations = 0x01,
};

uint8_t const *tud_descriptor_device_cb(void) {
    return (uint8_t const *) &desc_device;
}

/* ---------- Configuration Descriptor ---------- */

#define TUD_USBTMC_DESC_MAIN(_itfnum, _bNumEndpoints, _bulkMaxPacketLength) \
    TUD_USBTMC_IF_DESCRIPTOR(_itfnum, _bNumEndpoints, /*_stridx = */ 4u, TUD_USBTMC_PROTOCOL_USB488), \
    TUD_USBTMC_BULK_DESCRIPTORS(/* OUT = */ 0x01, /* IN = */ 0x81, /* packet size = */ _bulkMaxPacketLength)

#if CFG_TUD_USBTMC_ENABLE_INT_EP
#define TUD_USBTMC_DESC(_itfnum, _bulkMaxPacketLength) \
    TUD_USBTMC_DESC_MAIN(_itfnum, /* _epCount = */ 3, _bulkMaxPacketLength), \
    TUD_USBTMC_INT_DESCRIPTOR(/* INT ep # */ 0x82, /* epMaxSize = */ 8, /* bInterval = */ 16u)
#define TUD_USBTMC_DESC_LEN \
    (TUD_USBTMC_IF_DESCRIPTOR_LEN + TUD_USBTMC_BULK_DESCRIPTORS_LEN + TUD_USBTMC_INT_DESCRIPTOR_LEN)
#else
#define TUD_USBTMC_DESC(_itfnum, _bulkMaxPacketLength) \
    TUD_USBTMC_DESC_MAIN(_itfnum, /* _epCount = */ 2u, _bulkMaxPacketLength)
#define TUD_USBTMC_DESC_LEN \
    (TUD_USBTMC_IF_DESCRIPTOR_LEN + TUD_USBTMC_BULK_DESCRIPTORS_LEN)
#endif

enum { ITF_NUM_USBTMC, ITF_NUM_TOTAL };

#define CONFIG_TOTAL_LEN    (TUD_CONFIG_DESC_LEN + TUD_USBTMC_DESC_LEN)

uint8_t const desc_fs_configuration[] = {
    TUD_CONFIG_DESCRIPTOR(1, ITF_NUM_TOTAL, 0, CONFIG_TOTAL_LEN, 0x00, 100),
    TUD_USBTMC_DESC(ITF_NUM_USBTMC, /* _bulkMaxPacketLength = */ 64),
};

uint8_t const *tud_descriptor_configuration_cb(uint8_t index) {
    (void) index;
    return desc_fs_configuration;
}

/* ---------- String Descriptors ---------- */

enum {
    STRID_LANGID = 0,
    STRID_MANUFACTURER,
    STRID_PRODUCT,
    STRID_SERIAL,
    STRID_USBTMC_INTERFACE,
};

char const *string_desc_arr[] = {
    (const char[]) {0x09, 0x04},   // 0: English (0x0409)
    "PMVB",                         // 1: Manufacturer
    "PMVB Pico 2 W USB-TMC Stub",   // 2: Product
    NULL,                           // 3: Serial (populated from chip ID at runtime)
    "PMVB USB-TMC",                 // 4: USB-TMC interface label
};

static uint16_t _desc_str[32 + 1];

uint16_t const *tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
    (void) langid;
    size_t chr_count;

    switch (index) {
        case STRID_LANGID:
            memcpy(&_desc_str[1], string_desc_arr[0], 2);
            chr_count = 1;
            break;

        case STRID_SERIAL:
            /* board_usb_get_serial() pulls the 64-bit unique chip ID from the
             * RP2350 and formats it as a 16-char hex string into the UTF-16
             * descriptor buffer. This is the serial that PyVISA discovery
             * keys off (per SDD §10.1). */
            chr_count = board_usb_get_serial(_desc_str + 1, 32);
            break;

        default:
            if (!(index < sizeof(string_desc_arr) / sizeof(string_desc_arr[0]))) {
                return NULL;
            }
            const char *str = string_desc_arr[index];
            chr_count = strlen(str);
            size_t const max_count = sizeof(_desc_str) / sizeof(_desc_str[0]) - 1;
            if (chr_count > max_count) chr_count = max_count;
            for (size_t i = 0; i < chr_count; i++) {
                _desc_str[1 + i] = str[i];
            }
            break;
    }

    _desc_str[0] = (uint16_t) ((TUSB_DESC_STRING << 8) | (2 * chr_count + 2));
    return _desc_str;
}
