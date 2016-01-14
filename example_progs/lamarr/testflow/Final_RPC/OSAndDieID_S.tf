hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_EVEN";
  "Pins" = "SHRT_EVEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_10:
  "Limit_names" = "I_B_OPEN_PINS";
  "Pins" = "OPEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_12:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";
tm_2:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_EVEN";
  "Pins" = "SHRT_EVEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_3:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_EVEN";
  "Pins" = "SHRT_EVEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_4:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_EVEN";
  "Pins" = "SHRT_EVEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_5:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_ODD";
  "Pins" = "SHRT_ODD_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_6:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_ODD";
  "Pins" = "SHRT_ODD_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_7:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_ODD";
  "Pins" = "SHRT_ODD_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_8:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_B_SHRT_ODD";
  "Pins" = "SHRT_ODD_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_9:
  "Limit_names" = "I_B_OPEN_PINS";
  "Pins" = "OPEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_10:
  testmethod_class = "ti_tml.DC.Continuity_opens";
tm_11:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_12:
  testmethod_class = "ti_tml.DieID.PostReadDieID";
tm_2:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_3:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_4:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_5:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_6:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_7:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_8:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_9:
  testmethod_class = "ti_tml.DC.Continuity_opens";

end
-----------------------------------------------------------------
test_suites

DISCONNECT_Conty:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_11;
  site_control = "parallel:";
  site_match = 2;
DieIDPostRead_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 4;
  override_levset = 2;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_12;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = "1,1,1";
  site_control = "parallel:";
  site_match = 2;
PinOpensTestPerPin_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_10;
  override_tim_spec_set = "pALL_PLUS_DPS_WFT2_MPT";
  override_timset = "1";
  site_control = "parallel:";
  site_match = 2;
PinOpensTest_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_9;
  override_tim_spec_set = "pALL_PLUS_DPS_WFT2_MPT";
  override_timset = "1";
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_nIForce_Even:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_nIForce_Odd:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_pIForce_Even:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_4;
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_pIForce_Odd:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_8;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_nIForce_Even:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_nIForce_Odd:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_5;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_pIForce_Even:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_3;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_pIForce_Odd:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_testf = tm_7;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(PinShortsTest_st_nIForce_Even)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_nIForce_Even)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(PinShortsTest_st_pIForce_Even)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_pIForce_Even)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(PinShortsTest_st_nIForce_Odd)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_nIForce_Odd)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(PinShortsTest_st_pIForce_Odd)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_pIForce_Odd)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(PinOpensTest_st)
    then
    {
    }
    else
    {
       run_and_branch(PinOpensTestPerPin_st)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run(DISCONNECT_Conty);
    run_and_branch(DieIDPostRead_st)
    then
    {
    }
    else
    {
       multi_bin;
    }

  },open,"OSAndDieID_S",""

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
