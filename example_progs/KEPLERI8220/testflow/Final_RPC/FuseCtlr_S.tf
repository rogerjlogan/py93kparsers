hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "ComplementBurst" = "No";
  "ComplementBurstName" = "";
  "Corner" = "";
  "Dummy_label_name" = "";
  "Func_limit_name" = "EfuseInitCheck_limit";
  "Init_limit_name" = "";
  "Init_pattern" = "";
  "Interleave_init_pattern" = "No";
  "Mask_pins" = "No";
  "Masked_pins" = "";
  "Results_per_label" = "No";
  "Retest" = "No";
  "Site_match_mode" = "No";
  "SpeedSort" = "No";
  "SpeedSortAdaptiveSpec" = "No";
  "Stop_on_fail" = "No";
  "Util_purpose_off" = "";
  "Util_purpose_on" = "";
tm_2:
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
tm_3:
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
tm_4:
  "VDDCORE_Spec" = "VDDCORE_PS";
  "Vmax.Vmax1_Sets" = "";
  "Vmax.Vmax2_Sets" = "";
  "Vmax.Vmax3_Sets" = "";
  "Vmax.suite" = "";
  "Vmin.Vmin1_Sets" = "";
  "Vmin.Vmin2_Sets" = "SRVmin,SRVminDDR3L,VminVSROtlr";
  "Vmin.Vmin3_Sets" = "";
  "Vmin.suite" = "IddqVmin1_IqC08Ful_______KP11_000_st_PM1_MEAS";
  "Vnom.Vnom1_Sets" = "";
  "Vnom.Vnom2_Sets" = "";
  "Vnom.Vnom3_Sets" = "";
  "Vnom.suite" = "IddqVnom_IqC08Ful_______KP11_000_st_PM1_MEAS";

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
  testmethod_class = "ti_tml.SmartReflex.SR_SRc0PowerTest";

end
-----------------------------------------------------------------
test_suites

EfuseInitCheck_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 2;
  override_levset = 2;
  override_seqlbl = "InitCheck_MPB";
  override_testf = tm_1;
  override_tim_spec_set = "efuseInitcheck";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
EfuseRunAutoload_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_seqlbl = "RunAutoload_MPB";
  override_testf = tm_3;
  override_tim_spec_set = "pASYNC2_pASYNC3_pNONASYNC1_WFT38X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
FuseChainAddr_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 2;
  override_seqlbl = "EFUSE_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "pASYNC2_pASYNC3_pNONASYNC1_WFT38X4_MPT";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
SRc0PowerTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_4;
  override_tim_spec_set = "AC_per_10";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run_and_branch(EfuseInitCheck_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(FuseChainAddr_st)
    then
    {
    }
    else
    {
    }
    run_and_branch(EfuseRunAutoload_st)
    then
    {
    }
    else
    {
    }
    if @TITESTTYPE != "PB_RPC_LT" then
    {
       if @TITESTTEMP == "TEMP_25_DEG" then
       {
          print("Skipping Src0PowerTest since TITESTTEMP is 25");
          print_dl("Skipping Src0PowerTest since TITESTTEMP is 25");
       }
       else
       {
          run_and_branch(SRc0PowerTest)
          then
          {
          }
          else
          {
             multi_bin;
          }
       }
    }
    else
    {
    }

  },open,"FuseCtlr_S",""

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
