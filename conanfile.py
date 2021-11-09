import conans
import glob
import os
import shutil

from conans.errors import ConanInvalidConfiguration

class OpenH264Conan(conans.ConanFile):
    name = 'openh264'
    version = '2.1.1'
    settings = 'os', 'arch', 'build_type'
    python_requires = 'dockerRecipe/1.0.0@froglogic/util'
    python_requires_extend = 'dockerRecipe.DockerRecipe'
    win_bash = True
    revision_mode = 'scm'
    options = {
        'shared': [True, False],
    }
    default_options = {
        'shared': False,
    }
    scm = {
        'type': 'git',
        'url': 'auto',
        'revision': 'auto',
    }
    docker = {
        'Linux': {
            'image': '/squishbuild/centos6:6.8.0',
        },
    }

    def validate(self):
        if self.settings.os != 'Macos':
            if self.settings.arch.value not in ['x86_64', 'x86']:
                raise ConanInvalidConfiguration('Unsupported architecture: %s' % self.arch)

    def configure(self):
        if self.settings.os != 'Windows':
            self.build_requires = [ 'nasm/2.10.09@froglogic/util' ]
        if self.settings.os == 'Macos':
            del self.settings.arch

    def package_info(self):
        self.cpp_info.libdirs = ['lib']
        if self.settings.os == 'Windows' and self.options.shared:
            self.cpp_info.libs = ['openh264_dll']
        else:
            self.cpp_info.libs = ['openh264']

        if self.options.shared:
            return
        if self.settings.os != 'Windows':
            self.cpp_info.system_libs = ['stdc++']
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.extend(['m', 'pthread'])

    def buildWindows(self):
        msvcEnv = conans.client.tools.vcvars_dict(self, compiler_version='14')
        for name, value in msvcEnv.items():
            if isinstance(value, list):
                value = os.pathsep.join(value)
            os.environ[name] = value
        cmd = 'make -j%d OS=msvc ARCH=%s CFLAGS=-FS' % (conans.tools.cpu_count(), self.settings.arch)
        self.run(cmd)

    def buildMacos(self):
        if self.options.shared:
            type = 'shared'
            libname = 'libopenh264.%s.dylib' % self.version
        else:
            type = 'static'
            libname = 'libopenh264.a'
        self.run('make -j%d ARCH=x86_64' % conans.tools.cpu_count())
        self.run('make install-%s ARCH=x86_64 PREFIX=%s/x86_64' % (type, self.build_folder))
        self.run('make clean')
        self.run('make -j%d ARCH=arm64' % conans.tools.cpu_count())
        self.run('make install-%s ARCH=arm64 PREFIX=%s/arm64' % (type, self.build_folder))
        self.run('lipo x86_64/lib/{0} arm64/lib/{0} -create -output {0}'.format(libname))

    def buildLinux(self):
        paths = ['$PATH', *self.deps_cpp_info['nasm'].bin_paths]
        cmd = 'export PATH=' + ':'.join(paths) + '; '
        cmd += 'make -j%d ARCH=%s' % (conans.tools.cpu_count(), self.settings.arch)
        self.run(cmd)

    def build(self):
        getattr(self, 'build%s' % self.settings.os)()

    def packageMacos(self):
        libdir = os.path.join(self.package_folder, 'lib')
        if self.options.shared:
            libname = 'libopenh264.%s.dylib' % self.version
        else:
            libname = 'libopenh264.a'
        self.run('install -m 755 -d %s' % libdir)
        self.run('install -m 755 %s %s/%s' % (libname, libdir, libname))
        if self.options.shared:
            self.run('ln -s %s %s/libopenh264.6.dylib' % (libname, libdir))
            self.run('ln -s libopenh264.6.dylib %s/libopenh264.dylib' % libdir)
        self.run('make install-headers PREFIX=%s' % self.package_folder)

    def packageLinux(self):
        if self.options.shared:
            type = 'shared'
        else:
            type = 'static'
        self.run('make install-%s ARCH=%s PREFIX=%s' % (type, self.settings.arch, self.package_folder))
        self.run('make install-headers PREFIX=%s' % self.package_folder)

    def packageWindows(self):
        if self.options.shared:
            type = 'shared'
        else:
            type = 'static'
        package_folder = conans.tools.unix_path(self.package_folder, path_flavor='msys2')
        self.run('make install-%s OS=msvc ARCH=%s PREFIX=%s' % (type, self.settings.arch, package_folder))
        self.run('make install-headers OS=msvc PREFIX=%s' % package_folder)

    def package(self):
        getattr(self, 'package%s' % self.settings.os)()

