hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "VminDDR3L";
  "Dummy_label_name" = "";
  "Func_limit_name" = "X_MA_PHY_DDR_AC";
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
  "Corner" = "VminDDR3L";
  "Dummy_label_name" = "";
  "Func_limit_name" = "X_MA_PHY_DDR_AC_BU";
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
  "Corner" = "VminDDR3L";
  "Dummy_label_name" = "";
  "Func_limit_name" = "X_MA_PHY_DDR_DAT";
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

end
-----------------------------------------------------------------
test_suites

PHY_DDR_AC_AtSpeedVminDDR3L_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_seqlbl = "PHY_DDR_AC_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "pLOAD_pNOLOAD_pASYNC3_pASYNC4_pASYNC5_WFT5X8_4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PHY_DDR_AC_BU_AtSpeedVminDDR3L_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_seqlbl = "PHY_DDR_AC_BU_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "pLOAD_pNOLOAD_pASYNC3_pASYNC4_pASYNC5_WFT5X8_4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
PHY_DDR_DAT_AtSpeedVminDDR3L_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_seqlbl = "PHY_DDR_DAT_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "pLOAD_pNOLOAD_pASYNC3_pASYNC4_pASYNC5_WFT5X8_4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow
  {
    run_and_branch(PHY_DDR_AC_AtSpeedVminDDR3L_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run_and_branch(PHY_DDR_AC_BU_AtSpeedVminDDR3L_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
    run_and_branch(PHY_DDR_DAT_AtSpeedVminDDR3L_st)
    then
    {
    }
    else
    {
       multi_bin;
    }
  },open,"AtSpeedVminDDR3L_S",""

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
