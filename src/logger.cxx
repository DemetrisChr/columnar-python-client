/*
 *  Copyright 2016-2024. Couchbase, Inc.
 *  All Rights Reserved.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

#include "logger.hxx"

#include "exceptions.hxx"

PyTypeObject pycbcc_logger_type = { PyObject_HEAD_INIT(NULL) 0 };

static void
pycbcc_logger_dealloc(pycbcc_logger* self)
{
  Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject*
pycbcc_logger__configure_logging_sink__(PyObject* self, PyObject* args, PyObject* kwargs)
{
  auto logger = reinterpret_cast<pycbcc_logger*>(self);
  PyObject* pyObj_logger = nullptr;
  PyObject* pyObj_level = nullptr;
  const char* kw_list[] = { "logger", "level", nullptr };
  const char* kw_format = "OO";
  if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, kw_format, const_cast<char**>(kw_list), &pyObj_logger, &pyObj_level)) {
    pycbcc_set_python_exception(CoreClientErrors::VALUE,
                                __FILE__,
                                __LINE__,
                                "Cannot set pycbcc_logger sink.  Unable to parse args/kwargs.");
    return nullptr;
  }

  if (couchbase::core::logger::is_initialized()) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Cannot create logger.  Another logger has already been "
                    "initialized. Make sure the PYCBCC_LOG_LEVEL env "
                    "variable is not set if using configure_logging.");
    return nullptr;
  }

  if (pyObj_logger != nullptr) {
    logger->logger_sink_ = std::make_shared<pycbcc_logger_sink>(pyObj_logger);
  }

  couchbase::core::logger::configuration logger_settings;
  logger_settings.console = false;
  logger_settings.sink = logger->logger_sink_;
  auto level = convert_python_log_level(pyObj_level);
  logger_settings.log_level = level;
  couchbase::core::logger::create_file_logger(logger_settings);
  Py_RETURN_NONE;
}

PyObject*
pycbcc_logger__create_console_logger__(PyObject* self, PyObject* args, PyObject* kwargs)
{
  auto logger = reinterpret_cast<pycbcc_logger*>(self);
  char* log_level = nullptr;
  const char* kw_list[] = { "level", nullptr };
  const char* kw_format = "s";
  if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, kw_format, const_cast<char**>(kw_list), &log_level)) {
    pycbcc_set_python_exception(CoreClientErrors::VALUE,
                                __FILE__,
                                __LINE__,
                                "Cannot set create console logger.  Unable to parse args/kwargs.");
    return nullptr;
  }

  if (couchbase::core::logger::is_initialized()) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Cannot create logger.  Another logger has already been "
                    "initialized. Make sure to not use configure_logging if "
                    "going to set PYCBCC_LOG_LEVEL env.");
    return nullptr;
  }

  if (log_level == nullptr) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Cannot create console logger.  Unable to determine log level.");
    return nullptr;
  }
  couchbase::core::logger::create_console_logger();
  auto level = couchbase::core::logger::level_from_str(log_level);
  couchbase::core::logger::set_log_levels(level);

  Py_RETURN_NONE;
}

PyObject*
pycbcc_logger__enable_protocol_logger__(PyObject* self, PyObject* args, PyObject* kwargs)
{
  char* filename = nullptr;
  const char* kw_list[] = { "filename", nullptr };
  const char* kw_format = "s";
  if (!PyArg_ParseTupleAndKeywords(
        args, kwargs, kw_format, const_cast<char**>(kw_list), &filename)) {
    pycbcc_set_python_exception(CoreClientErrors::VALUE,
                                __FILE__,
                                __LINE__,
                                "Cannot enable the protocol logger.  Unable to parse args/kwargs.");
    return nullptr;
  }
  couchbase::core::logger::configuration configuration{};
  configuration.filename = std::string{ filename };
  couchbase::core::logger::create_protocol_logger(configuration);
  Py_RETURN_NONE;
}

static PyMethodDef pycbcc_logger_methods[] = {
  { "configure_logging_sink",
    (PyCFunction)pycbcc_logger__configure_logging_sink__,
    METH_VARARGS | METH_KEYWORDS,
    PyDoc_STR("Configure logger's logging sink") },
  { "create_console_logger",
    (PyCFunction)pycbcc_logger__create_console_logger__,
    METH_VARARGS | METH_KEYWORDS,
    PyDoc_STR("Create a console logger") },
  { "enable_protocol_logger",
    (PyCFunction)pycbcc_logger__enable_protocol_logger__,
    METH_VARARGS | METH_KEYWORDS,
    PyDoc_STR("Enables the protocol logger") },
  { NULL }
};

static PyObject*
pycbcc_logger_new(PyTypeObject* type, PyObject*, PyObject*)
{
  pycbcc_logger* self = reinterpret_cast<pycbcc_logger*>(type->tp_alloc(type, 0));
  return reinterpret_cast<PyObject*>(self);
}

int
pycbcc_logger_type_init(PyObject** ptr)
{
  PyTypeObject* p = &pycbcc_logger_type;

  *ptr = (PyObject*)p;
  if (p->tp_name) {
    return 0;
  }

  p->tp_name = "pycbcc_core.pycbcc_logger";
  p->tp_doc = "Python SDK Logger";
  p->tp_basicsize = sizeof(pycbcc_logger);
  p->tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
  p->tp_new = pycbcc_logger_new;
  p->tp_dealloc = (destructor)pycbcc_logger_dealloc;
  p->tp_methods = pycbcc_logger_methods;

  return PyType_Ready(p);
}

size_t
convert_spdlog_level(spdlog::level::level_enum lvl)
{
  // TODO:  support trace level in the python logger
  switch (lvl) {
    case spdlog::level::level_enum::off:
      return 0;
    case spdlog::level::level_enum::trace:
      return 5;
    case spdlog::level::level_enum::debug:
      return 10;
    case spdlog::level::level_enum::info:
      return 20;
    case spdlog::level::level_enum::warn:
      return 30;
    case spdlog::level::level_enum::err:
      return 40;
    case spdlog::level::level_enum::critical:
      return 50;
    default:
      return 0;
  }
}

couchbase::core::logger::level
convert_python_log_level(PyObject* level)
{
  auto lvl = PyLong_AsSize_t(level);
  switch (lvl) {
    case 0:
      return couchbase::core::logger::level::off;
    case 5:
      return couchbase::core::logger::level::trace;
    case 10:
      return couchbase::core::logger::level::debug;
    case 20:
      return couchbase::core::logger::level::info;
    case 30:
      return couchbase::core::logger::level::warn;
    case 40:
      return couchbase::core::logger::level::err;
    case 50:
      return couchbase::core::logger::level::critical;
    default:
      return couchbase::core::logger::level::off;
  }
}
