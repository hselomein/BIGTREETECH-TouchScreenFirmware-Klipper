Import("env")

build_flags = env.ParseFlags(env['BUILD_FLAGS'])
flags = {k: v for (k, v) in build_flags.get("CPPDEFINES")}
filename = flags.get("BINARY_FILENAME")
# set file name by hardware and firmware version
if filename == None:
    version = flags.get("SOFTWARE_VERSION")
    # Strip fork suffix (e.g. "28.x-klipper.2" -> "28.x") so the output filename
    # matches the exact format the TFT bootloader expects (HARDWARE.VERSION.bin).
    # The full version string is still compiled into the binary for the About screen.
    version = version.split("-")[0] if version and "-" in version else version
    filename = flags.get("HARDWARE") + "." + version
# rename firmware if portrait mode is selected
if flags.get("PORTRAIT_MODE") != None:
    filename = filename + flags.get("PORTRAIT_MODE")

env.Replace(PROGNAME = filename)
