#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string>

std::string judge(const std::string& );

static PyObject *
judge(PyObject *self, PyObject *args)
{
    const char *input_str;

    if (!PyArg_ParseTuple(args, "s", &input_str))
        return NULL;
	
	// 可以释放全局锁，并在结尾收回。但由于主进程是单线程的，这个优化没有用，反而可能引入不稳定性（反正我崩过），所以注释掉
	// Py_BEGIN_ALLOW_THREADS
	
	std::string input(input_str);
    std::string output = judge(input);
	
	// Py_END_ALLOW_THREADS
	
    return PyUnicode_FromString(output.c_str());
}

static const char* judge_lib_doc = "python wrapper for judge";

static PyMethodDef JudgeLibMethods[] = {
    {"judge", judge, METH_VARARGS,
     "judge json_str and return json_str"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef judge_lib_module = {
    PyModuleDef_HEAD_INIT,
    "judge_lib",   /* 模块名称 */
    judge_lib_doc, /* 模块文档，可以为 NULL */
    -1,       /* 模块的每解释器状态大小，
                 或者如果模块在全局变量中状态则为 -1。 */
    JudgeLibMethods
};


PyMODINIT_FUNC
PyInit_judge_lib(void)
{
    PyObject *m;

    m = PyModule_Create(&judge_lib_module);
    if (m == NULL)
        return NULL;

    return m;
}