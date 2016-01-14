hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "Limit_names" = "I_LB_OPEN_PINS";
  "Pins" = "OPEN_PINS";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_2:
  "Limit_names" = "I_LB_OPEN_PINS,I_LB_OPEN_PINS_gpio11";
  "Pins" = "OPEN_PINS,gpio11";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_3:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";
tm_4:
  "Limit_names" = "I_LB_OPEN_PINS";
  "Pins" = "OPEN_DCsig";
  "SettlingTime_ms" = "3";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_5:
  "Limit_names" = "I_LB_OPEN_PINS";
  "Pins" = "OPEN_DCsig";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_6:
  "Limit_names" = "I_LB_OPEN_PINS";
  "Pins" = "OPEN_DCsig";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_7:
  "Limit_names" = "I_LB_OPEN_PINS";
  "Pins" = "OPEN_DCsig";
  "SettlingTime_ms" = "1";
  "TestCurrent_uA" = "-10";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_8:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "";
  "Dummy_label_name" = "";
  "Func_limit_name" = "";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "No";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.DC.Continuity_opens";
tm_2:
  testmethod_class = "ti_tml.DC.Continuity_opens";
tm_3:
  testmethod_class = "ti_tml.DieID.PostReadDieID";
tm_4:
  testmethod_class = "ti_tml.DC.Continuity_Opens_DCsig";
tm_5:
  testmethod_class = "ti_tml.DC.Continuity_Opens_DCsig";
tm_6:
  testmethod_class = "ti_tml.DC.Continuity_Opens_DCsig";
tm_7:
  testmethod_class = "ti_tml.DC.Continuity_Opens_DCsig";
tm_8:
  testmethod_class = "ti_tml.Digital.Functional";

end
-----------------------------------------------------------------
test_suites

DCPinOpensTestPerPin_st_nIForce_SigGroup:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_7;
  site_control = "parallel:";
  site_match = 2;
DCPinOpensTestPerPin_st_pIForce_SigGroup:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_5;
  site_control = "parallel:";
  site_match = 2;
DCPinOpensTest_st_nIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_6;
  site_control = "parallel:";
  site_match = 2;
DCPinOpensTest_st_pIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_4;
  site_control = "parallel:";
  site_match = 2;
DieIDPreRead_Open_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 1;
  override_seqlbl = "Read_Norm_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PinOpensTestPerPin_st_nIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 2;
PinOpensTest_st_nIForce:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 3;
  override_levset = 2;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
SupplyOpensTest_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 27;
  override_levset = 2;
  override_seqlbl = "DUMMY_DEF_BURST";
  override_testf = tm_8;
  override_tim_equ_set = 1;
  override_tim_spec_set = 1;
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(PinOpensTest_st_nIForce)
    then
    {
    }
    else
    {
       run_and_branch(PinOpensTestPerPin_st_nIForce)
       then
       {
       }
       else
       {
          run_and_branch(DieIDPreRead_Open_st)
          then
          {
          }
          else
          {
          }
          multi_bin;
       }
    }
    run_and_branch(DCPinOpensTest_st_pIForce)
    then
    {
    }
    else
    {
       run_and_branch(DCPinOpensTestPerPin_st_pIForce_SigGroup)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(DCPinOpensTest_st_nIForce)
    then
    {
    }
    else
    {
       run_and_branch(DCPinOpensTestPerPin_st_nIForce_SigGroup)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    run_and_branch(SupplyOpensTest_st)
    then
    {
    }
    else
    {
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
