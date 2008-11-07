# vim:tw=0:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
cmos_obj:
    python interface to functions in libsmbios_c  obj/cmos.h
"""

# imports (alphabetical)
import ctypes
import exceptions

from _common import *
from trace_decorator import decorate, traceLog, getLog

__all__ = ["CmosAccess", "CMOS_DEFAULTS", "CMOS_GET_SINGLETON", "CMOS_GET_NEW", "CMOS_UNIT_TEST_MODE"]

CMOS_DEFAULTS      =0x0000
CMOS_GET_SINGLETON =0x0001
CMOS_GET_NEW       =0x0002
CMOS_UNIT_TEST_MODE=0x0004

decorate(traceLog())
def CmosAccess(flags=CMOS_GET_SINGLETON, factory_args=None):
    if factory_args is None: factory_args = []
    if _CmosAccess._instance is None:
        _CmosAccess._instance = _CmosAccess( flags, *factory_args)
    return _CmosAccess._instance

class _CmosAccess(object):
    _instance = None

    decorate(traceLog())
    def __init__(self, *args):
        self._cmosobj = None
        self._cmosobj = _libsmbios_c.cmos_obj_factory(*args)

    decorate(traceLog())
    def __del__(self):
        _libsmbios_c.cmos_obj_free(self._cmosobj)

    decorate(traceLog())
    def readByte(self, offset, indexPort, dataPort):
        buf = ctypes.c_uint8
        _libsmbios_c.cmos_obj_read(self._cmosobj, buf, offset, length)
        return buf

    decorate(traceLog())
    def writeByte(self, offset, indexPort, dataPort):
        _libsmbios_c.cmos_obj_write(self._cmosobj, buf, offset, len(buf))



# initialize libsmbios lib
_libsmbios_c = ctypes.cdll.LoadLibrary("libsmbios_c.so.2")

#struct cmos_access_obj;
class _cmos_access_obj(ctypes.Structure): pass

#// format error string
#const char *cmos_obj_strerror(const struct cmos_access_obj *m);
# define strerror first so we can use it in error checking other functions.
_libsmbios_c.cmos_obj_strerror.argtypes = [ ctypes.POINTER(_cmos_access_obj) ]
_libsmbios_c.cmos_obj_strerror.restype = ctypes.c_char_p
decorate(traceLog())
def _strerror(obj):
    return Exception(_libsmbios_c.cmos_obj_strerror(obj))

#struct cmos_access_obj *cmos_obj_factory(int flags, ...);
# dont define argtypes because this is a varargs function...
#_libsmbios_c.cmos_obj_factory.argtypes = [ctypes.c_int, ]
_libsmbios_c.cmos_obj_factory.restype = ctypes.POINTER(_cmos_access_obj)
_libsmbios_c.cmos_obj_factory.errcheck = errorOnNullPtrFN(lambda r,f,a: _strerror(r))

#void   cmos_obj_free(struct cmos_access_obj *);
_libsmbios_c.cmos_obj_free.argtypes = [ ctypes.POINTER(_cmos_access_obj) ]
_libsmbios_c.cmos_obj_free.restype = None

#int     cmos_obj_read_byte(const struct cmos_access_obj *, u8 *byte, u32 indexPort, u32 dataPort, u32 offset);
_libsmbios_c.cmos_obj_read_byte.argtypes = [ ctypes.POINTER(_cmos_access_obj), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32 ]
_libsmbios_c.cmos_obj_read_byte.restype = ctypes.c_int
_libsmbios_c.cmos_obj_read_byte.errcheck = errorOnNegativeFN(_strerror)

#int    cmos_obj_write_byte(const struct cmos_access_obj *, u8 byte,  u32 indexPort, u32 dataPort, u32 offset);
_libsmbios_c.cmos_obj_write_byte.argtypes = [ ctypes.POINTER(_cmos_access_obj), ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32 ]
_libsmbios_c.cmos_obj_write_byte.restype = ctypes.c_int
_libsmbios_c.cmos_obj_write_byte.errcheck = errorOnNegativeFN(_strerror)


#// useful for checksums, etc
#typedef int (*cmos_write_callback)(const struct cmos_access_obj *, bool, void *);
#void cmos_obj_register_write_callback(struct cmos_access_obj *, cmos_write_callback, void *, void (*destruct)(void *));
#int cmos_obj_run_callbacks(const struct cmos_access_obj *m, bool do_update);


