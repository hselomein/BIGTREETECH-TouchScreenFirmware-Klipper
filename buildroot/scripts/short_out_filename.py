Import("env")
import os
import shutil

def make_short_file(source, target, env):
    print("Generating firmware with short file name...")
    repo_path = os.path.realpath("")
    build_dir = env.subst('$BUILD_DIR')
    filename = env['PROGNAME'] + ".bin"
    src_file_path = os.path.join(repo_path, build_dir, filename)
    build_flags = env.ParseFlags(env['BUILD_FLAGS'])
    flags = {k: v for (k, v) in build_flags.get("CPPDEFINES")}
    version_short = flags.get("SOFTWARE_VERSION_SHORT")
    version_short = version_short.split("-")[0] if version_short and "-" in version_short else version_short
    filename_short = flags.get("HARDWARE_SHORT") + version_short + ".new"
    target_file_path = os.path.join(repo_path, build_dir, filename_short)
    shutil.copyfile(src_file_path, target_file_path)
    print("Done.")

env.AddPostAction("buildprog", make_short_file)
