hp93000,testflow,0.1
language_revision = 1;

information

end
-----------------------------------------------------------------
declarations

@my_double = 2.333;
@my_string = "this is my string";
end
-----------------------------------------------------------------
implicit_declarations

end
-----------------------------------------------------------------
flags

datalog_formatter = 0;
datalog_sample_size = 1;
graphic_result_displa = 1;
state_display = 0;
print_wafermap = 0;
ink_wafer = 0;
max_reprobes = 1;
temp_monitor = 1;
calib_age_monitor = 1;
diag_monitor = 1;
current_monitor = 1;
log_events_enable = 1;
set_pass_level = 0;
set_fail_level = 0;
set_bypass_level = 0;
hold_on_fail = 0;
global_hold = 0;
debug_mode = 0;
debug_analog = 0;
parallel_mode = 1;
site_match_mode = 2;
global_overon = 0;
limits_enable = 0;
test_number_enable = 1;
test_number_inc = 1;
log_cycles_before = 0;
log_cycles_after = 0;
unburst_mode = 0;
sqst_mode = 0;
warn_as_fail = 1;
use_hw_dsp = 0;
dsp_file_enable = 0;
buffer_testflow_log = 0;
check_testmethod_api = 0;
stdf_generation = 1;
tm_crash_as_fatal = 1;
hidden_datalog_mode = 0;
multibin_mode = 0;
user	my_inc_var = 0;
user	my_userflag = 1;
end
-----------------------------------------------------------------
testmethodparameters
tm_1:
  "testName" = "Functional";
  "output" = "None";
tm_10:
  "testName" = "Functional";
  "output" = "None";
tm_11:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_12:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
tm_13:
  "testName" = "Functional";
  "output" = "None";
tm_14:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_15:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
tm_16:
  "testName" = "Functional";
  "output" = "None";
tm_17:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_18:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
tm_2:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_3:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
tm_4:
  "testName" = "Functional";
  "output" = "None";
tm_5:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_6:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
tm_7:
  "testName" = "Functional";
  "output" = "None";
tm_8:
  "scanPins" = "@";
  "maxFailsPerPin" = "-1";
  "cycleBased" = "1";
  "includeExpectedData" = "0";
  "testerCycleMode" = "1";
  "output" = "None";
  "cycleNumberPerLabel" = "false";
  "testName" = "ScanTest";
tm_9:
  "dpsPins" = "@";
  "constantCurrent" = "OFF";
  "unregulated" = "OFF";
  "overVoltage" = "OFF";
  "overPowerTemp" = "OFF";
  "protect" = "OFF";
  "testName" = "DPS_Status";
  "output" = "None";
end
-----------------------------------------------------------------
testmethodlimits
tm_1:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_10:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_11:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_12:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
tm_13:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_14:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_15:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
tm_16:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_17:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_18:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
tm_2:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_3:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
tm_4:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_5:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_6:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
tm_7:
  "Functional" = "":"NA":"":"NA":"":"":"";
tm_8:
  "ScanTest" = "":"NA":"":"NA":"":"":"";
tm_9:
  "DPS_Status" = "":"NA":"":"NA":"":"":"";
end
-----------------------------------------------------------------
testmethods
tm_1:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_10:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_11:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_12:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
tm_13:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_14:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_15:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
tm_16:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_17:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_18:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
tm_2:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_3:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
tm_4:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_5:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_6:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
tm_7:
  testmethod_class = "ac_tml.AcTest.FunctionalTest";
tm_8:
  testmethod_class = "scan_tml.ScanTest.ScanTest";
tm_9:
  testmethod_class = "dc_tml.DcTest.DpsStatus";
end
-----------------------------------------------------------------
test_suites
test1:
  override = 1;
 override_testf = tm_1;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test1_1:
  override = 1;
 override_testf = tm_4;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test1_2:
  override = 1;
 override_testf = tm_7;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test1_3:
  override = 1;
 override_testf = tm_10;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test1_4:
  override = 1;
 override_testf = tm_13;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test1_5:
  override = 1;
 override_testf = tm_16;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2:
  override = 1;
 override_testf = tm_2;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2_1:
  override = 1;
 override_testf = tm_5;
local_flags  = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2_2:
  override = 1;
 override_testf = tm_8;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2_3:
  override = 1;
 override_testf = tm_11;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2_4:
  override = 1;
 override_testf = tm_14;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test2_5:
  override = 1;
 override_testf = tm_17;
local_flags  = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3:
  override = 1;
 override_testf = tm_3;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3_1:
  override = 1;
 override_testf = tm_6;
local_flags  = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3_2:
  override = 1;
 override_testf = tm_9;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3_3:
  override = 1;
 override_testf = tm_12;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3_4:
  override = 1;
 override_testf = tm_15;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
test3_5:
  override = 1;
 override_testf = tm_18;
local_flags  = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
 site_match = 2;
 site_control = "parallel:";
end
-----------------------------------------------------------------
test_flow

 run(test1);
 run_and_branch(test2)
 then
 {
 }
 else
 {
 }
 run_and_branch(test3)
 then
 {
 }
 else
 {
    multi_bin;
 }
 {
    run(test1_4);
    run_and_branch(test2_4)
    then
    {
    }
    else
    {
    }
    run_and_branch(test3_4)
    then
    {
    }
    else
    {
       multi_bin;
    }
    {
       run(test1_5);
       run_and_branch(test2_5)
       then
       {
       }
       else
       {
       }
       run_and_branch(test3_5)
       then
       {
       }
       else
       {
          multi_bin;
       }
       {
          run(test1_1);
          run_and_branch(test2_1)
          then
          {
          }
          else
          {
          }
          run_and_branch(test3_1)
          then
          {
          }
          else
          {
             multi_bin;
          }
       }, open,"subgroup2-1", ""
       {
          run(test1_2);
          run_and_branch(test2_2)
          then
          {
          }
          else
          {
          }
          run_and_branch(test3_2)
          then
          {
          }
          else
          {
             multi_bin;
          }
       }, groupbypass, open,"subgroup2-2", ""
    }, open,"subgroup1-1", ""
    {
       run(test1_3);
       run_and_branch(test2_3)
       then
       {
       }
       else
       {
       }
       run_and_branch(test3_3)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }, open,"subgroup1-2", ""
 }, open,"group1", ""
 print("this is a print string expr");
 print_dl("this is print to dlog string expr");
 if @my_inc_var == 1 then
 {
 }
 else
 {
    stop_bin "12", "bad_sbin12", , bad, noreprobe, red, 10, over_on;
 }
 repeat
until @my_inc_var > 5
 test_number_loop_increment = 0
 while @my_inc_var < 6 do
 test_number_loop_increment = 0
 {
 }
 for @my_inc_var = 1; @my_inc_var < 10 ; @my_inc_var = @my_inc_var + 1; do
 test_number_loop_increment = 0
 {
 }
 @my_inc_var = 0;
 svlr_level_command(1,1,"VDD_PS",1);
 svlr_timing_command(-999,"TimSpec1","freq@portALL",120);
 {
    stop_bin "1", "good_sbin1", , good, noreprobe, green, 1, over_on;
 }, open,"goodbin_group", ""
end
-----------------------------------------------------------------
binning
otherwise bin = "db", "", , bad, noreprobe, red, , not_over_on;
end
-----------------------------------------------------------------
context

end
-----------------------------------------------------------------
hardware_bin_descriptions
  1 = "good_hbin1";
  10 = "bad_hbin10";
end
