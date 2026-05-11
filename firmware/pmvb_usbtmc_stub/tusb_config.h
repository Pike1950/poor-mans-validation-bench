/*
 * TinyUSB configuration for the PMVB USB-TMC stub firmware.
 *
 * Phase 0 probe firmware: one USB-TMC interface with USB488 subclass for
 * SCPI-compliant behavior. No CDC / MSC / HID / etc. The interrupt endpoint
 * is enabled so the host can poll for service requests.
 */

#ifndef TUSB_CONFIG_H_
#define TUSB_CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif

#ifndef BOARD_TUD_RHPORT
#define BOARD_TUD_RHPORT      0
#endif

#ifndef BOARD_TUD_MAX_SPEED
#define BOARD_TUD_MAX_SPEED   OPT_MODE_DEFAULT_SPEED
#endif

// CFG_TUSB_MCU is provided by the Pico SDK's CMake glue based on PICO_PLATFORM.
#ifndef CFG_TUSB_MCU
#error CFG_TUSB_MCU must be defined (Pico SDK should provide this; check CMake setup)
#endif

#ifndef CFG_TUSB_OS
#define CFG_TUSB_OS           OPT_OS_PICO
#endif

#ifndef CFG_TUSB_DEBUG
#define CFG_TUSB_DEBUG        0
#endif

// Enable device stack
#define CFG_TUD_ENABLED       1
#define CFG_TUD_MAX_SPEED     BOARD_TUD_MAX_SPEED

#ifndef CFG_TUSB_MEM_SECTION
#define CFG_TUSB_MEM_SECTION
#endif

#ifndef CFG_TUSB_MEM_ALIGN
#define CFG_TUSB_MEM_ALIGN    __attribute__ ((aligned(4)))
#endif

#ifndef CFG_TUD_ENDPOINT0_SIZE
#define CFG_TUD_ENDPOINT0_SIZE    64
#endif

// USB-TMC class config (USB488 subclass = SCPI-compliant)
#define CFG_TUD_USBTMC                1
#define CFG_TUD_USBTMC_ENABLE_INT_EP  1
#define CFG_TUD_USBTMC_ENABLE_488     1

#ifdef __cplusplus
}
#endif

#endif /* TUSB_CONFIG_H_ */
