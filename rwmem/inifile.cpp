#include <exception>
#include <cstdlib>
#include <cstdio>
#include <cstring>

#include "inireader.h"
#include "rwmem.h"
#include "helpers.h"

using namespace std;

INIReader rwmem_ini;

static string detect_platform()
{
	string result;

	try {
		string det = rwmem_ini.get("main", "detect");

		FILE* pipe = popen(det.c_str(), "r");

		if (pipe == nullptr)
			throw exception();

		char buffer[256];

		if (fgets(buffer, sizeof(buffer), pipe) != nullptr)
			result = string(buffer, strlen(buffer) - 1);

		pclose(pipe);
	} catch (...) {

	}

	return result;
}

void load_opts_from_ini()
{
	vprint("Reading settings from rwmem.ini\n");

	unsigned rs = rwmem_ini.get_int("main", "regsize", rwmem_opts.regsize * 8);

	if (rs != 8 && rs != 16 && rs != 32 && rs != 64)
		ERR("Invalid size '%d'", rs);

	rwmem_opts.regsize = rs / 8;

	rwmem_opts.platform = detect_platform();

	string plat_key = string("platform \"") + rwmem_opts.platform + "\"";
	rwmem_opts.regfile = rwmem_ini.get(plat_key, "regfile", "");
}
