import subprocess
import sys


def fix(s):
    # We use Clang 3.7 for generating bytecode but take CFLAGS from current compiler
    # We should filter new flags unknown to the old compiler
    if s == '-Wno-undefined-var-template':
        return None

    # disable dbg DEVTOOLS-2744
    if s == '-g':
        return None
    if s == '/Z7':
        return None

    # disable sanitizers for generated code
    if s.startswith('-fsanitize') or s == '-Dmemory_sanitizer_enabled' or s.startswith('-fsanitize-blacklist'):
        return None

    # Paths under .ya/tools/v3/.../msvc/include are divided with '\'
    return s.replace('\\', '/')


def fix_path(p):
    try:
        i = p.rfind('/bin/clang')
        p = p[:i] + '/bin/clang-cl'
    except ValueError:
        pass
    return p


if __name__ == '__main__':
    is_on_win = sys.argv[1] == 'yes'
    path = sys.argv[2]
    args = filter(None, [fix(s) for s in sys.argv[3:]])
    if is_on_win:
        path = fix_path(path)
        try:
            i = args.index('-emit-llvm')
            args[i:i+1] = ['-Xclang', '-emit-llvm']
        except ValueError:
            pass
        args.append('-fms-compatibility-version=19')

    cmd = [path] + args

    rc = subprocess.call(cmd, shell=False, stderr=sys.stderr, stdout=sys.stdout)
    sys.exit(rc)

