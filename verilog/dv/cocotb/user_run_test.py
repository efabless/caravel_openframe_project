from caravel_cocotb.scripts.verify_cocotb.RunTest import RunTest


class UserRunTest(RunTest):
    def __init__(self, args, paths, test, logger) -> None:
        super().__init__(args, paths, test, logger)

    def hex_riscv_command_gen(self):
        # paths that need to be changed
        FIRMWARE_PATH = f"{self.paths.USER_PROJECT_ROOT}/verilog/dv/firmware"
        self.test.linker_script_file = f"{FIRMWARE_PATH}/sections.lds"
        GCC_PATH = "/foss/tools/riscv-gnu-toolchain-rv32i/217e7f3debe424d61374d31e33a091a630535937/bin/"
        GCC_PATH = "/opt/riscv/bin/"
        GCC_PREFIX = "riscv32-unknown-linux-gnu"
        GCC_COMPILE = f"{GCC_PATH}/{GCC_PREFIX}"
        SOURCE_FILES = f"{FIRMWARE_PATH}/custom_ops.S {FIRMWARE_PATH}/start.S {FIRMWARE_PATH}/irq.c "
        LINKER_SCRIPT = f"-Wl,-Bstatic,-T,{self.test.linker_script_file},--strip-debug "
        CPUFLAGS = "-g -march=rv32imc -mabi=ilp32 -ffreestanding -nostdlib"
        includes = f" -I{FIRMWARE_PATH} -I{self.paths.USER_PROJECT_ROOT}/verilog/dv/cocotb "
        macros = "-DUSE_IRQ_FUNCTION -Os" if "irq" in self.test.name else ""  # TODO: for future fix -Os is used here because of the without it the irq function write to illegal memory and with it the uart test fails
        elf_command = (
            f"{GCC_COMPILE}-gcc  {macros} {includes} {CPUFLAGS} {LINKER_SCRIPT}"
            f" -o {self.hex_dir}/{self.test.name}.elf {SOURCE_FILES} {self.c_file}"
        )
        lst_command = f"{GCC_COMPILE}-objdump -d -S {self.hex_dir}/{self.test.name}.elf > {self.hex_dir}/{self.test.name}.lst "
        hex_command = f"{GCC_COMPILE}-objcopy -O verilog {self.hex_dir}/{self.test.name}.elf {self.hex_dir}/{self.test.name}.hex "
        sed_command = f'sed -ie "s/@10/@00/g" {self.hex_dir}/{self.test.name}.hex'
        return f" {elf_command} && {lst_command} && {hex_command} && {sed_command}"

    def write_vcs_includes_file(self):
        self.vcs_dirs = ""
        self.generate_includes()

    def write_iverilog_includes_file(self):
        self.generate_includes()

    def generate_includes(self):
        if self.test.sim == "RTL":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.rtl.caravel_user_project"
        elif self.test.sim == "GL":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.gl.caravel_user_project"
        elif self.test.sim == "GL_SDF":
            include_list = f"{self.paths.USER_PROJECT_ROOT}/verilog/includes/includes.gl+sdf.caravel_user_project"
        includes_files = ""
        with open(include_list, "r") as f:
            for line in f:
                # Remove leading and trailing whitespace
                line = line.strip()
                # Check if line is not empty or a comment
                if line and not line.startswith("#"):
                    # Replace $(VERILOG_PATH) with actual path
                    line = line.replace("$(VERILOG_PATH)", self.paths.VERILOG_PATH)
                    line = line.replace("$(CARAVEL_PATH)", self.paths.CARAVEL_PATH)
                    line = line.replace(
                        "$(USER_PROJECT_VERILOG)",
                        f"{self.paths.USER_PROJECT_ROOT}/verilog",
                    )
                    line = line.replace("$(PDK_ROOT)", f"{self.paths.PDK_ROOT}")
                    line = line.replace("$(PDK)", f"{self.paths.PDK}")
                    # Extract file path from command
                    if line.startswith("-v"):
                        file_path = line.split(" ")[1]
                        includes_files += f'`include "{file_path}"\n'
        self.test.includes_file = f"{self.test.compilation_dir}/includes.v"
        open(self.test.includes_file, "w").write(includes_files)
