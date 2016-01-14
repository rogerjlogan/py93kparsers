hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "VskewPhiOD";
  "Dummy_label_name" = "";
  "Func_limit_name" = "XM_OWA_PB_PLL_VSKEW";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_2:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "VskewPhiOD";
  "Dummy_label_name" = "";
  "Func_limit_name" = "XM_OWA_PB_PLL_VSKEW_1";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_3:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "VskewPhiOD";
  "Dummy_label_name" = "";
  "Func_limit_name" = "XM_OWA_PB_PLL_VSKEW_2";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_4:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "VskewPhiOD";
  "Dummy_label_name" = "";
  "Func_limit_name" = "XM_OWA_PB_PLL_VSKEW_3";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "Yes";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "";
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
  testmethod_class = "ti_tml.Digital.Functional";
tm_2:
  testmethod_class = "ti_tml.Digital.Functional";
tm_3:
  testmethod_class = "ti_tml.Digital.Functional";
tm_4:
  testmethod_class = "ti_tml.Digital.Functional";

end
-----------------------------------------------------------------
test_suites

PB_PLL_VSKEW_1_AtSpeedVskewPhiOD_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 24;
  override_levset = 3;
  override_seqlbl = "PB_PLL_VSKEW_1_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT8X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PB_PLL_VSKEW_2_AtSpeedVskewPhiOD_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 24;
  override_levset = 3;
  override_seqlbl = "PB_PLL_VSKEW_2_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT9X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PB_PLL_VSKEW_3_AtSpeedVskewPhiOD_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 24;
  override_levset = 3;
  override_seqlbl = "PB_PLL_VSKEW_3_MPB";
  override_testf = tm_4;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT6X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PB_PLL_VSKEW_AtSpeedVskewPhiOD_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 24;
  override_levset = 3;
  override_seqlbl = "PB_PLL_VSKEW_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "pASYNC1_pASYNC2_pNONASYNC1_WFT7X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(PB_PLL_VSKEW_AtSpeedVskewPhiOD_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(PB_PLL_VSKEW_1_AtSpeedVskewPhiOD_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(PB_PLL_VSKEW_2_AtSpeedVskewPhiOD_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(PB_PLL_VSKEW_3_AtSpeedVskewPhiOD_st)
    then
    {
    }
    else
    {
    }

  },open,"AtSpeedVskewPhiOD_S",""

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
