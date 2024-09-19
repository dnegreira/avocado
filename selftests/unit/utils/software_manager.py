import os
import unittest

from avocado.utils import distro
from avocado.utils.software_manager import backends, manager
from selftests.utils import BASEDIR, setup_avocado_loggers

setup_avocado_loggers()


def apt_supported_distro():
    """Distros we expect to have the apt backend selected."""
    return distro.detect().name in ["debian", "Ubuntu"]


def isfloat(version):
    """Simple method to verify if a value can be converted to a float"""
    try:
        float(version)
        return True
    except ValueError:
        return False


def login_binary_path(distro):
    """Retrieve the login binary path based on the distro version"""
    detected = distro.detect()
    if detected.name == "Ubuntu":
        if float(detected.version) >= 24.04:
            return "/usr/bin/login"
    if detected.name == "debian":
        if isfloat(detected.version):
            if float(detected.version >= 13):
                return "/usr/bin/login"
        if detected.version == "sid":
            return "/usr/bin/login"
    return "/bin/login"


@unittest.skipUnless(os.getuid() == 0, "This test requires root privileges")
@unittest.skipUnless(apt_supported_distro(), "Unsupported distro")
class Apt(unittest.Test):
    def test_provides(self):
        sm = manager.SoftwareManager()
        login_path = login_binary_path(distro)
        self.assertEqual(sm.provides(login_path), "login")
        self.assertTrue(isinstance(sm.backend, backends.apt.AptBackend))


class Dpkg(unittest.TestCase):
    def test_is_valid(self):
        deb_path = os.path.join(BASEDIR, "selftests", ".data", "hello.deb")
        dpkg = backends.dpkg.DpkgBackend
        self.assertTrue(dpkg.is_valid(deb_path))

    def test_is_not_valid(self):
        not_deb_path = os.path.join(BASEDIR, "selftests", ".data", "guaca.a")
        dpkg = backends.dpkg.DpkgBackend
        self.assertFalse(dpkg.is_valid(not_deb_path))


if __name__ == "__main__":
    unittest.main()
