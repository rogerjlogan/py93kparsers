hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "START";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";
tm_2:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "1";
  "Enable Cooling" = "1";
  "Enable Heating" = "1";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "-30";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_UHD_C3_3_PG_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "START DATALOG CTCS";
  "Time Between TD Reading" = "2";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
tm_3:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "PURGE";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
tm_4:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "PURGE";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
tm_5:
  "Enable Efuse Burning" = "1";
  "Force to burn temp1" = "0";
  "Pattern name to get sensor" = "temp_sen_calib_MP";
  "Sensor Selection" = "BOTH";
  "Static Temperature or Therm Diode" = "DIODE";
  "Temperature use for Sensors Calibration" = "30";
tm_6:
  "Control Temperature" = "0";
  "Diode Selection" = "DIODE2";
  "Diodes Pins List" = "thermdiodea1,thermdiodea1";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "Pattern name to get sensor" = "temp_sen_calib_MP";
  "Re-initialized Thermal setup" = "1";
  "Relays Purpose Pins List Off" = "Therm1_DC_off,Therm1_DC_on";
  "Relays Purpose Pins List On" = "Therm1_DC_on,Therm1_DC_on";
  "Sensor Selection" = "BOTH";
  "Time Between TD Reading" = "1";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
tm_7:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "1";
  "Enable Cooling" = "1";
  "Enable Heating" = "1";
  "End Of Flow Warm Up Time Out" = "30";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "dummy_pNONASYNC1_MP";
  "Pattern name to warm up device" = "PB_PLL_UHD_C3_3_PG_MPB";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "STOP DATALOG CTCS";
  "Time Between TD Reading" = "10";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_2:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_3:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_4:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_5:
  testmethod_class = "ti_tml.Thermal.Thermal_Calibration";
tm_6:
  testmethod_class = "ti_tml.Thermal.Thermal_Reading";
tm_7:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";

end
-----------------------------------------------------------------
test_suites

CTCS_Purge_CT_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 8;
  override_levset = 2;
  override_seqlbl = "PB_PLL_RTA_M0_1_PG_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
CTCS_Purge_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 8;
  override_levset = 2;
  override_seqlbl = "PB_PLL_UHD_C3_3_PG_MPB";
  override_testf = tm_4;
  override_tim_spec_set = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
CTCS_START_Thermal:
  comment = "Reset CTCS and TD Min/Max";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 2;
CTCS_Start_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_testf = tm_1;
  override_tim_spec_set = "Thermo_Sensors";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
CTCS_Thermal:
  comment = "Read CTCS Min/MAx and datalof it with TD Min/Max since reset";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_testf = tm_7;
  override_tim_spec_set = "Thermo_Sensors";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
Thermo_Sensors_Calibration:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_testf = tm_5;
  override_tim_spec_set = "Thermo_Sensors";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
Thermo_Sensors_Read_Temperature:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 2;
  override_testf = tm_6;
  override_tim_spec_set = "Thermo_Sensors";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(CTCS_Start_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run_and_branch(CTCS_START_Thermal)
    then
    {
    }
    else
    {
    }
    if @TITESTTYPE == "PB_RPC_LT" then
    {
       run_and_branch(CTCS_Purge_CT_st)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    else
    {
       run_and_branch(CTCS_Purge_st)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(Thermo_Sensors_Calibration)
    then
    {
    }
    else
    {
    }
    run_and_branch(Thermo_Sensors_Read_Temperature)
    then
    {
    }
    else
    {
    }
    run_and_branch(CTCS_Thermal)
    then
    {
    }
    else
    {
    }

  },open,"Thermal_S",""

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
