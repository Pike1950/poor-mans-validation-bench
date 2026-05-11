cmake_minimum_required(VERSION 3.13)

# Pull in the Pico SDK. PICO_SDK_PATH is set in ~/.bashrc by the orchestration
# bring-up procedure; on a fresh machine, export it to point at the cloned
# pico-sdk tree before invoking cmake.
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(pmvb_usbtmc_stub C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Default to Pico 2 W if the caller did not pass -DPICO_BOARD on the cmake line.
# The bench bring-up procedure exports PICO_BOARD=pico2_w in ~/.bashrc.
if(NOT DEFINED PICO_BOARD)
    set(PICO_BOARD "pico2_w")
endif()

pico_sdk_init()

add_executable(pmvb_usbtmc_stub
    main.c
    usb_descriptors.c
    usbtmc_handlers.c
)

target_include_directories(pmvb_usbtmc_stub PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(pmvb_usbtmc_stub PRIVATE
    pico_stdlib
    pico_unique_id
    tinyusb_device
    tinyusb_board
)

# This firmware uses the USB interface for USB-TMC, not stdio. Route any
# stdio (printf debugging) over UART instead.
pico_enable_stdio_usb(pmvb_usbtmc_stub 0)
pico_enable_stdio_uart(pmvb_usbtmc_stub 1)

# Produce .uf2 (for drag-drop flashing) alongside .elf/.bin/.hex/.dis
pico_add_extra_outputs(pmvb_usbtmc_stub)
