hp93000,testflow,0.1
language_revision = 1;

information

device_name = "74145";

device_revision = "1";

test_revision = "1";

description = "The 74145 is a BCD-to-Decimal Converter";

end
--------------------------------------------------
declarations

end
--------------------------------------------------
flags
report_to_file = 1;
report_to_printer = 0;
datalog_to_file = 1;
datalog_to_printer = 0;
datalog_to_report_win = 0;
datalog_formatter = 0;
datalog_sample_size = 1;
graphic_result_displa = 1;
state_display = 0;
print_wafermap = 0;
OOC_watch = 1;
OOC_sample_size = 1;
ink_wafer = 0;
max_reprobes = 1;
temp_monitor = 1;
calib_age_monitor = 1;
diag_monitor = 1;
current_monitor = 1;
set_pass_level = 0;
set_fail_level = 0;
set_bypass_level = 0;
hold_on_fail = 0;
optimized_mode = 1;
global_hold = 0;
debug_mode = 0;
parallel_mode = 1;
global_overon = 0;
end
--------------------------------------------------
testfunctions
tf_1:
testfunction_description = "Continuity";
testfunction_parameters = "continuity;@;0;uA; 10;mV; 200;mV;
	700;mV; 900;ms;1;0;Continuity ($P);";

tf_6:
testfunction_description = "Basic functional test";
testfunction_parameters = "functional";

end
--------------------------------------------------
test_suites
Continuity:
override = 1;
override_wvfset = 1;
override_timset = 1;
override_levset = 1;
override_dpsset = 1;
override_seqlbl = "DEFAULT";
override_testf = tf_1;
Basic_functional_tes:
override = 1;
override_wvfset = 1;
override_timset = 1;
override_levset = 1;
override_dpsset = 1;
override_seqlbl = "DEFAULT";
override_testf = tf_6;
end
--------------------------------------------------
test_flow

run_and_branch(Continuity) then
{
}
else
{
stop_bin "AA", "Continuity failed", , bad,noreprobe,red, ,over_on;
}
run_and_branch(Basic_functional_tes) then
{
}
else
{
stop_bin "BB", "Basic functional test failed", ,bad,noreprobe,red, ,over_on;
}
stop_bin "OK", "Everything went fine", , good,noreprobe,
green, , over_on;
end
-------------------------------------------------
binning

otherwise bin = "db", "", , bad,noreprobe,red, , not_over_on;
end
-------------------------------------------------
oocrule


end
-------------------------------------------------
context

context_config_file = "74145";
context_levels_file = "LowPower";
context_timing_file = "Fast";
context_vector_file = "74145";
context_attrib_file = "";
context_mixsgl_file = "";

end
--------------------------------------------------