/*
 * PMVB USB-TMC stub firmware - entry point.
 *
 * Phase 0 probe firmware that flashes onto a bare Pico 2 W and makes it
 * enumerate as a USB-TMC instrument with a chip-ID-derived serial number,
 * suitable for the SDD §10.1 hot-plug-by-serial verification milestone.
 *
 * Not a per-module SCPI parser. Real module firmware ships per-phase.
 */

#include "bsp/board_api.h"
#include "tusb.h"

extern void pmvb_usbtmc_init(void);
extern void pmvb_usbtmc_task_iter(void);

int main(void) {
    board_init();
    pmvb_usbtmc_init();

    tusb_rhport_init_t dev_init = {
        .role = TUSB_ROLE_DEVICE,
        .speed = TUSB_SPEED_AUTO,
    };
    tusb_init(BOARD_TUD_RHPORT, &dev_init);

    if (board_init_after_tusb) {
        board_init_after_tusb();
    }

    while (true) {
        tud_task();              // TinyUSB device task
        pmvb_usbtmc_task_iter(); // handles deferred BOOTSEL reset
    }
}

/* ---------- USB device-level callbacks ----------
 * These are required by TinyUSB but we have no LED to blink and no state to
 * track at this layer. Kept as no-ops. */

void tud_mount_cb(void)    { }
void tud_umount_cb(void)   { }
void tud_suspend_cb(bool remote_wakeup_en) { (void) remote_wakeup_en; }
void tud_resume_cb(void)   { }
