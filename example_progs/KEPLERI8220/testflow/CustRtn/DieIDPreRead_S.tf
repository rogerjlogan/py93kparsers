hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_LB_SHRT_EVEN,I_LB_SHRT_ODD";
  "Pins" = "SHRT_EVEN,SHRT_ODD";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_3:
  "Execution Mode" = "Serial";
  "Limit_names" = "I_LB_SHRT_EVEN,I_LB_SHRT_ODD";
  "Pins" = "SHRT_EVEN,SHRT_ODD";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_4:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";
tm_5:
  "Execution Mode" = "Parallel";
  "Limit_names" = "I_LB_SHRT_EVEN,I_LB_SHRT_ODD";
  "Pins" = "SHRT_EVEN,SHRT_ODD";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_6:
  "Execution Mode" = "Serial";
  "Limit_names" = "I_LB_SHRT_EVEN,I_LB_SHRT_ODD";
  "Pins" = "SHRT_EVEN,SHRT_ODD";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_7:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";
tm_9:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_10:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_3:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_4:
  testmethod_class = "ti_tml.DieID.PostReadDieID";
tm_5:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_6:
  testmethod_class = "ti_tml.DC.Continuity_shorts";
tm_7:
  testmethod_class = "ti_tml.DieID.PostReadDieID";
tm_8:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_9:
  testmethod_class = "ti_tml.DieID.PostReadDieID";

end
-----------------------------------------------------------------
test_suites

DISCONNECT_3:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_4:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_8;
  site_control = "parallel:";
  site_match = 2;
DISCONNECT_4_2:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_10;
  site_control = "parallel:";
  site_match = 2;
DieIDPreRead_Shortn_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 1;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_4;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
DieIDPreRead_Shortp_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 1;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_7;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
DieIDPreRead_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 1;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_9;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_nIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_3;
  site_control = "parallel:";
  site_match = 2;
PinShortsTestPerPin_st_pIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_nIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 2;
PinShortsTest_st_pIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_5;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(DISCONNECT_3);
    run_and_branch(PinShortsTest_st_nIForce)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_nIForce)
       then
       {
       }
       else
       {
          run_and_branch(DieIDPreRead_Shortn_st)
          then
          {
          }
          else
          {
          }
          multi_bin;
       }
    }
    run_and_branch(PinShortsTest_st_pIForce)
    then
    {
    }
    else
    {
       run_and_branch(PinShortsTestPerPin_st_pIForce)
       then
       {
       }
       else
       {
          run_and_branch(DieIDPreRead_Shortp_st)
          then
          {
          }
          else
          {
          }
          multi_bin;
       }
    }
    run(DISCONNECT_4);
    run_and_branch(DieIDPreRead_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run(DISCONNECT_4_2);

  },open,"DieIDPreRead_S",""

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
