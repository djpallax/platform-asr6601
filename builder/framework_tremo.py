from SCons.Script import Import
import os
import glob

Import("env")

# -----------------------------------------------------------------------------
# Force ARM GCC toolchain
# -----------------------------------------------------------------------------
env.Replace(
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    AS="arm-none-eabi-gcc",
    AR="arm-none-eabi-ar",
    OBJCOPY="arm-none-eabi-objcopy",
    OBJDUMP="arm-none-eabi-objdump",
    SIZE="arm-none-eabi-size"
)

# -----------------------------------------------------------------------------
# Resolve framework path
# -----------------------------------------------------------------------------
framework_path = env.GetProjectOption("asr_framework_path")

if not framework_path:
    print("ERROR: asr_framework_path not defined in platformio.ini")
    env.Exit(1)

if not os.path.isdir(framework_path):
    print("ERROR: framework path does not exist:", framework_path)
    env.Exit(1)

print("Using ASR framework at:", framework_path)

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
cmsis      = os.path.join(framework_path, "CMSIS")
system     = os.path.join(framework_path, "system")
drivers    = os.path.join(framework_path, "drivers")
periph_inc = os.path.join(drivers, "peripheral", "inc")
periph_src = os.path.join(drivers, "peripheral", "src")
crypto_inc = os.path.join(drivers, "crypto", "inc")
crypto_lib = os.path.join(drivers, "crypto", "lib")

ldscript   = os.path.join(framework_path, "ldscripts", "gcc.ld")

# -----------------------------------------------------------------------------
# Includes
# -----------------------------------------------------------------------------
env.Append(
    CPPPATH=[
        cmsis,
        system,
        periph_inc,
        crypto_inc,
    ]
)

# -----------------------------------------------------------------------------
# Compiler flags
# -----------------------------------------------------------------------------
env.Append(
    CCFLAGS=[
        "-Wall",
        "-Os",
        "-mcpu=cortex-m4",
        "-mthumb",
        "-mfpu=fpv4-sp-d16",
        "-mfloat-abi=softfp",
        "-ffunction-sections",
        "-fdata-sections",
        "-std=gnu99",
        "-fno-builtin-printf",
        "-fno-builtin-sprintf",
        "-fno-builtin-snprintf",
    ]
)

# -----------------------------------------------------------------------------
# Assembler flags (IMPORTANT for startup_cm4.S)
# -----------------------------------------------------------------------------
env.Append(
    ASFLAGS=[
        "-mcpu=cortex-m4",
        "-mthumb",
        "-mfpu=fpv4-sp-d16",
        "-mfloat-abi=softfp",
    ]
)

# -----------------------------------------------------------------------------
# Linker
# -----------------------------------------------------------------------------
env.Replace(LDSCRIPT_PATH=ldscript)

env.Append(
    LINKFLAGS=[
        "-T" + ldscript,
        "-Wl,--gc-sections",
        "-mcpu=cortex-m4",
        "-mthumb",
        "-mfpu=fpv4-sp-d16",
        "-mfloat-abi=softfp"
    ]
)

# -----------------------------------------------------------------------------
# Build system sources (exclude printf by default)
# -----------------------------------------------------------------------------
env.BuildSources(
    os.path.join(env.subst("$BUILD_DIR"), "framework", "system"),
    system,
    src_filter=[
        "+<*>",
        "-<printf-stdarg.c>"
    ]
)

# -----------------------------------------------------------------------------
# Optional printf support
# -----------------------------------------------------------------------------
use_printf = env.GetProjectOption("use_printf", "no").lower() == "yes"

if use_printf:
    print("ASR: printf support ENABLED")

    env.Append(
        CPPDEFINES=["USE_PRINTF"],
        LINKFLAGS=[
            "-Wl,--wrap=printf",
            "-Wl,--wrap=sprintf",
            "-Wl,--wrap=snprintf",
        ]
    )

    # Compile printf-stdarg.c as an object
    printf_obj = env.Object(
        target=os.path.join(env.subst("$BUILD_DIR"), "framework", "system", "printf-stdarg.o"),
        source=os.path.join(system, "printf-stdarg.c")
    )

    # Add the object to the build files
    env.Append(PIOBUILDFILES=[printf_obj])

else:
    print("ASR: printf support DISABLED")

# -----------------------------------------------------------------------------
# Peripheral drivers
# -----------------------------------------------------------------------------
env.BuildSources(
    os.path.join(env.subst("$BUILD_DIR"), "framework", "peripheral"),
    periph_src
)

# -----------------------------------------------------------------------------
# Crypto static library
# -----------------------------------------------------------------------------
env.Append(
    LIBPATH=[crypto_lib],
    LIBS=["crypto"]
)

# -----------------------------------------------------------------------------
# Debug UART selection (CONFIG_DEBUG_UART)
# -----------------------------------------------------------------------------
debug_uart = env.GetProjectOption("debug_uart", "UART0")  # default
# generate -DCONFIG_DEBUG_UART=UART0 
env.Append(CPPDEFINES=[("CONFIG_DEBUG_UART", debug_uart)])
print("ASR: debug uart =", debug_uart)

# -----------------------------------------------------------------------------
# Project sources
# -----------------------------------------------------------------------------
env.BuildSources(
    os.path.join(env.subst("$BUILD_DIR"), "src"),
    env.subst("$PROJECT_SRC_DIR")
)

## -----------------------------------------------------------------------------
# Link final program (ELF)
# -----------------------------------------------------------------------------
elf = env.Program(
    target=env.subst("$BUILD_DIR/${PROGNAME}.elf"),
    source=env["PIOBUILDFILES"]
)

env.Default(elf)

# -----------------------------------------------------------------------------
# Generate BIN (target real)
# -----------------------------------------------------------------------------
bin_path = env.subst("$BUILD_DIR/${PROGNAME}.bin")

target_bin = env.Command(
    bin_path,
    elf,
    env.VerboseAction(
        "$OBJCOPY -O binary $SOURCE $TARGET",
        "Generating BIN from ELF"
    )
)

env.Default(elf, target_bin)

# -----------------------------------------------------------------------------
# Upload using tremo_loader.py from platformio
# -----------------------------------------------------------------------------
platform_dir = env.PioPlatform().get_dir()
loader_py = os.path.join(platform_dir, "builder", "scripts", "tremo_loader.py")

# Defaults
upload_port = str(env.GetProjectOption("upload_port", env.get("UPLOAD_PORT", ""))).strip()
upload_speed = str(env.GetProjectOption("upload_speed", env.get("UPLOAD_SPEED", "921600"))).strip()

if not upload_port:
    print("ERROR: upload_port no está definido (ej: /dev/ttyUSB0)")
    env.Exit(1)

flash_addr = env.BoardConfig().get("upload.offset_address", "0x08000000")

upload_cmd = (
    '"$PYTHONEXE" "%s" -p "%s" -b "%s" flash %s "%s"'
    % (loader_py, upload_port, upload_speed, flash_addr, bin_path)
)

env.AddCustomTarget(
    name="upload",
    dependencies=target_bin,
    actions=env.VerboseAction(upload_cmd, "Uploading firmware"),
    title="Upload",
    description="Upload firmware via tremo_loader over UART"
)