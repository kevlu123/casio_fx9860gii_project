import os
import sys
import shutil
import glob
import json
from pathlib import Path

project = json.load(open("project.json"))
title = project["title"]
addin_icon = project["addin_icon"]
eactivity_icon = project["eactivity_icon"]
c_source = [os.path.basename(f)[:-2] for f in glob.glob("src/*.c")]
cpp_source = [os.path.basename(f)[:-4] for f in glob.glob("src/*.cpp")]

def abs_path(path):
    return os.path.abspath(path).replace(" ", "\\ ")

def write_lines(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines))

def mkdir(path):
    Path(path).mkdir(exist_ok=True)

def execute(*cmd, run_in=None, env=None, ignore_errors=False):
    print("Command: ", " ".join(cmd))

    if run_in is not None:
        cwd = os.getcwd()
        os.chdir(run_in)

    if env is not None:
        for key, value in env.items():
            os.environ[key] = value

    if ec := os.system(" ".join(cmd)) and not ignore_errors:
        print("Exited with", int(ec))
        exit(ec)

    if run_in is not None:
        os.chdir(cwd)

def clean():
    shutil.rmtree("ide", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)

def generate_addininfo(folder):
    write_lines(folder + "/AddinInfo.txt", [
        f'//------------------------------------------------------------------',
        f'// Addin-Application header control file, created with the CASIO SDK',
        f'//------------------------------------------------------------------',
        f'[OUTPUT]     : "{title}.g1a"',
        f'[BINDATA]    : "FXADDINror.bin"',
        f'[DISPNAME]   : "{title}"',
        f'[APPNAME]    : "@{title}"',
        f'[VERSION]    : "01.00.0000"',
        f'[APL_ICON]   : "{addin_icon}"',
        f'[MODULE_NUM] : 0',
        f'[MOD1_TITLE] : "{title}"',
        f'[MOD1_ICON]  : "{eactivity_icon}"'
    ])

def generate_ide_files():
    generate_addininfo("ide")

    shutil.copyfile(addin_icon, "ide/" + os.path.basename(addin_icon))
    shutil.copyfile(eactivity_icon, "ide/" + os.path.basename(eactivity_icon))

    write_lines(f"ide/{title}.g1w", [
        f"[DLSimProject]",
        f"Name={title}",
        f"Version=1",
        f"Model=:fx-9860G.dlm",
        f"SourcePath=SRC",
        f"MemoryPath=INIT",
        f"MemCardPath=SDCard",
        f"",
        f"[Program1]",
        f"Program={title}.G1A",
        f"Debug=../build/FXADDINror.dbg",
        f"LoadAddress=80000000:90100000",
        f"",
        f"[Files]",
        *[f"SourceFile=:../src/{s}.c" for s in c_source],
        *[f"SourceFile=:../src/{s}.cpp" for s in cpp_source],
    ])
    
def compile(file, lang):
    basename = abs_path("build/" + file)
    execute(
	    "shc.exe",
        "-cpu=sh3",
        "-include=" + abs_path("tools/fxinclude"),
        f"-objectfile={basename}.obj",
        "-show=source",
        "-listfile=" + abs_path(f"build/debug/{file}.lst"),
        "-size",
        "-noinline",
        "-chgincpath",
        "-errorpath",
        abs_path("src/" + file),
        f"-lang={lang}",
        "-nologo",
        "-debug",
        run_in="tools/shbin",
        env={
            "SHC_INC": abs_path("tools/shinclude"),
            #"PATH=$(TCDIR)\bin
            "SHC_LIB": abs_path("tools/shbin"),
            "SHC_TMP": abs_path("build"),
        }
    )

def link():
    write_lines("build/link.cmd", [
        "noprelink",
        "sdebug",
        "rom D=R",
        "nomessage ",
        "list " + abs_path("build/debug/FXADDINror.map"),
        "show symbol",
        "nooptimize",
        "start P_TOP,P,C,D,C$VTBL,C$INIT/0300200,B_BR_Size,B,R/08100000",
        "fsymbol P",
        "nologo",
        "input " + " ".join(abs_path(f"build/{s}.obj") for s in (c_source + cpp_source)),
        "input " + abs_path("tools/fxlib/setup.obj"),
        "library " + abs_path("tools/fxlib/fx9860G_library.lib"),
        "output " + abs_path("build/FXADDINror.abs"),
        "-nomessage=1100",
        "end",
        "input " + abs_path("build/FXADDINror.abs"),
        "form binary",
        "output " + abs_path("build/debug/FXADDINror.bin"),
        "exit"
    ])

    execute(
	    "Optlnk.exe -subcommand=" + abs_path("build/link.cmd"),
        run_in="tools/shbin"
    )

def package():
    shutil.copyfile(addin_icon, "build/" + addin_icon)
    shutil.copyfile(eactivity_icon, "build/" + eactivity_icon)

    generate_addininfo("build")

    execute(
        "MakeAddinHeader363.exe",
        abs_path("build"),
        run_in="tools",
        ignore_errors=True
    )

    shutil.copyfile(f"build/{title}.g1a", f"ide/{title}.g1a")

def main():
    os.chdir(Path(__file__).parent)

    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: python build.py <options>")
        print("  -h --help      Show this help message")
        print("  -c --clean     Clean the project")
        print("  -p --cpp       Compile .c files as C++")
        exit()

    if "-c" in sys.argv or "--clean" in sys.argv:
        clean()
        exit()

    if " " in abs_path("."):
        print("Error: Please move the project to a path without spaces.")
        exit(1)

    mkdir("ide")
    mkdir("ide/src")
    mkdir("build")
    mkdir("build/debug")

    generate_ide_files()

    as_cpp = "-p" in sys.argv or "--cpp" in sys.argv
    for file in c_source:
        compile(file, "cpp" if as_cpp else "c")
    for file in cpp_source:
        compile(file, "cpp")
    link()
    package()

if __name__ == "__main__":
    main()
