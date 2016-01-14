hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "DPS_disconnect_pinlist" = "";
  "DPS_setVoltages" = "0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115,0.0115";
  "Limit_names" = "I_B_SP_VDDDDR,I_B_SP_VDDPLL,I_B_SP_VDDIO,I_B_SP_VDDNWA,I_B_SP_VDDPLL,I_B_SP_VDDRAM,I_B_SP_VDDSHI,I_B_SP_VDDSLO,I_B_SP_VDDUHI,I_B_SP_VDDULO,I_B_SP_VPP,I_B_SP_VDDCORE";
  "Perform_functional_pretest" = "No";
  "Pins" = "VDDDDR,VDDDPLL,VDDIO,VDDNWA,VDDPLL,VDDRAM,VDDSHI,VDDSLO,VDDUHI,VDDULO,VPP,VDDCORE";
  "Power_of_2_number_of_samples" = "16";
  "Wait_time_ms" = "35";
tm_3:
  "instName" = "TIDieID";
  "readPST" = "FF_Read_Norm";
tm_4:
  "DPS_disconnect_pinlist" = "";
  "DPS_setVoltages" = "0.01";
  "Limit_names" = "";
  "Perform_functional_pretest" = "Yes";
  "Pins" = "";
  "Power_of_2_number_of_samples" = "16";
  "Wait_time_ms" = "2";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.DC.Supply_shorts";
tm_3:
  testmethod_class = "ti_tml.DieID.PostReadDieID";
tm_4:
  testmethod_class = "ti_tml.DC.Supply_shorts";

end
-----------------------------------------------------------------
test_suites

DISCONNECT:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
DieIDPreRead_SupplyShort_st:
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
SupplyShortsPre2_st:
  local_flags = bypass, output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 27;
  override_levset = 2;
  override_testf = tm_4;
  override_tim_equ_set = 1;
  override_tim_spec_set = 1;
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
SupplyShortsPre_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 2;
  override_lev_spec_set = 2;
  override_levset = 2;
  override_testf = tm_2;
  override_tim_spec_set = "AC_per_33_12";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(DISCONNECT);
    run_and_branch(SupplyShortsPre_st)
    then
    {
    }
    else
    {
       run_and_branch(DieIDPreRead_SupplyShort_st)
       then
       {
       }
       else
       {
       }
       multi_bin;
    }
    run_and_branch(SupplyShortsPre2_st)
    then
    {
    }
    else
    {
    }

  },open,"SupplyShortsPre_S",""

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
