hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "BoardSerNo" = "A123456";
  "BomNoRev" = "61234567";
tm_4:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "INIT";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";
tm_5:
  "Auto Tune PID temperature" = "-40";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "TUNE";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";
tm_6:
  "Auto Tune PID temperature" = "0";
  "Control Temperature" = "0";
  "Enable Cooling" = "0";
  "Enable Heating" = "0";
  "Lower Limit Range Offset Temperature" = "0";
  "Pattern name to cool down device" = "";
  "Pattern name to warm up device" = "";
  "SPT OFFSET" = "0";
  "Thermo Control Mode" = "ENDOFLOT";
  "Time Between TD Reading" = "1";
  "Upper Limit Range Offset Temperature" = "0";
  "WarmUpLevelsCorner" = "Vmin";
  "WarmUpLevelset" = "2";
  "WarmUpTimingSet" = "1";
  "WarmUpTimingSpecName" = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT_AtSpeedVmax";

end
-----------------------------------------------------------------
testmethodlimits

tm_2:
  "USP_READ_EEPROM" = "1":"GE":"1":"LE":"":"1":"1";

end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "USP_EEPROM64K.EepromClass.USP_WRITE_24C64";
tm_2:
  testmethod_class = "USP_EEPROM64K.EepromClass.USP_READ_24C64";
tm_3:
  testmethod_class = "ti_tml.Misc.Check_eeprom_against_testflow";
tm_4:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_5:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";
tm_6:
  testmethod_class = "ti_tml.Thermal.Thermal_Control";

end
-----------------------------------------------------------------
test_suites

CTCS_Auto_Tune_PID_st:
  comment = "Auto tune the PID";
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 6;
  override_levset = 2;
  override_seqlbl = "PB_PLL_UHD_C3_3_PG_MPB";
  override_testf = tm_5;
  override_tim_spec_set = "a99pASY1_pASY5_pASY3nALT_pNONASYNC1_WFT5X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
CTCS_End_Of_Lot_st:
  comment = "End of lot CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
CTCS_Init_st:
  comment = "Start CTCS";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_4;
  site_control = "parallel:";
  site_match = 2;
Loadboard_eeprom_check:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_3;
  site_control = "parallel:";
  site_match = 2;
USP_READ_EEPROM:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_test_number = 5;
  override_testf = tm_2;
  site_control = "parallel:";
USP_WRITE_EEPROM:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_test_number = 5;
  override_testf = tm_1;
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
       run(USP_WRITE_EEPROM);
       run(USP_READ_EEPROM);
       run_and_branch(Loadboard_eeprom_check)
       then
       {
       }
       else
       {
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
          run_and_branch(CTCS_Auto_Tune_PID_st)
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
             stop_bin "1", "GOOD_UNIT", , good, noreprobe, green, 1, not_over_on;
          }
          else
          {
          }
       }
       stop_bin "1", "GOOD_UNIT", , good, noreprobe, green, 1, not_over_on;
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
