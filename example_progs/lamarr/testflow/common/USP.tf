hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "dpsPins" = "VDDDDR,VDDDPLL,VDDIO,VDDNWA,VDDPLL,VDDRAM,VDDSHI,VDDSLO,VDDUHI,VDDULO,VPP";
  "output" = "None";
  "testName" = "DPS_ForceSense";
tm_2:
  "BoardSerNo" = "W151802";
  "BomNoRev" = "6589847A";
tm_4:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_GEM_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "INIT";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "pASYNC1_pASYNC2_pNONASYNC1_WFT7X4_MPT";
tm_5:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_UHD_C3_3_PG_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "ENDOFLOT";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";
tm_6:
  "dpsPins" = "VDDCORE";
  "output" = "None";
  "testName" = "DPS_ForceSense";
tm_7:
  "Control Temperature" = "0";
  "Diode Selection" = "DIODE2";
  "Diodes Pins List" = "thermdiodea1,thermdiodea1";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "Pattern name to get sensor" = "temp_sensor_MPB";
  "Re-initialized Thermal setup" = "1";
  "Relays Purpose Pins List Off" = "Therm1_DC_off,Therm1_DC_off";
  "Relays Purpose Pins List On" = "Therm1_DC_on,Therm1_DC_on";
  "Sensor Selection" = "NONE";
  "Time Between TD Reading" = "1";
  "WarmUpLevelsCorner" = "VminOD";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "Therm_Sensor_spec";
tm_8:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_GEM_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "INIT";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "pASYNC1_pASYNC2_pNONASYNC1_WFT7X4_MPT";
tm_9:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_UHD_C3_3_PG_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "READ";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";

end
-----------------------------------------------------------------
testmethodlimits

tm_1:
  "DPS_ForceSense" = "":"NA":"":"NA":"":"":"";
tm_3:
  "USP_READ_EEPROM" = "1":"GE":"1":"LE":"":"1":"1";
tm_6:
  "DPS_ForceSense" = "":"NA":"":"NA":"":"":"";

end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "dc_tml.DcTest.DpsConnectivity";
tm_10:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_11:
  testmethod_class = "ti_tml.BBT.SetupBBT";
tm_2:
  testmethod_class = "USP_EEPROM64K.EepromClass.USP_WRITE_24C64";
tm_3:
  testmethod_class = "USP_EEPROM64K.EepromClass.USP_READ_24C64";
tm_4:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_5:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_6:
  testmethod_class = "dc_tml.DcTest.DpsConnectivity";
tm_7:
  testmethod_class = "ti_tml.Thermal.Thermal_Reading";
tm_8:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_9:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";

end
-----------------------------------------------------------------
test_suites

CTCS_End_Of_Lot_st:
  comment = "End of lot CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_5;
  site_control = "parallel:";
  site_match = 2;
CTCS_Init_manual_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_8;
  site_control = "parallel:";
  site_match = 2;
CTCS_Init_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_4;
  site_control = "parallel:";
  site_match = 2;
CTCS_Read_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_9;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_1:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_10;
  site_control = "parallel:";
  site_match = 2;
DPS128Connectivity:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
SetupBBT_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 11;
  override_levset = 2;
  override_testf = tm_11;
  site_control = "parallel:";
  site_match = 2;
Thermal_init:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_7;
  override_tim_spec_set = "Thermal_Sensor_spec";
  override_timset = "1,1,1";
  site_control = "parallel:";
  site_match = 2;
UHC4Connectivity:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
USP_READ_EEPROM:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_test_number = 5;
  override_testf = tm_3;
  site_control = "parallel:";
USP_WRITE_EEPROM:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_test_number = 5;
  override_testf = tm_2;
  site_control = "parallel:";

end
-----------------------------------------------------------------
test_flow

  {
    if @USP_BRCONTROL == "main" then
    {
    }
    else
    {
       run_and_branch(DPS128Connectivity)
       then
       {
       }
       else
       {
          stop_bin "97", "F_DPS128_Connectivity", , bad, noreprobe, red, 8, not_over_on;
       }
       run_and_branch(USP_WRITE_EEPROM)
       then
       {
       }
       else
       {
       }
       run_and_branch(USP_READ_EEPROM)
       then
       {
       }
       else
       {
          stop_bin "98", "F_LOADBOARDCHK_SBIN", , bad, noreprobe, red, 7, not_over_on;
       }
       if @USP_CTCS_CONTROL == "start" then
       {
          run_and_branch(CTCS_Init_st)
          then
          {
          }
          else
          {
          }
       }
       else
       {
          if @USP_CTCS_CONTROL == "stop" then
          {
             run_and_branch(CTCS_End_Of_Lot_st)
             then
             {
             }
             else
             {
             }
             stop_bin "1", "PASS", , good, noreprobe, green, 1, not_over_on;
          }
          else
          {
          }
       }
       stop_bin "1", "PASS", , good, noreprobe, green, 1, not_over_on;
    }
    run_and_branch(UHC4Connectivity)
    then
    {
    }
    else
    {
       stop_bin "96", "F_UHC4_Connectivity", , bad, noreprobe, red, 8, not_over_on;
    }
    run_and_branch(Thermal_init)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run_and_branch(CTCS_Init_manual_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(CTCS_Read_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run(DISCONNECT_1);
    run_and_branch(SetupBBT_st)
    then
    {
    }
    else
    {
       multi_bin;
    }

  },open,"USP",""

end
-----------------------------------------------------------------
binning
end
-----------------------------------------------------------------
oocrule


end
-----------------------------------------------------------------
context


end
-----------------------------------------------------------------
hardware_bin_descriptions


end
-----------------------------------------------------------------
