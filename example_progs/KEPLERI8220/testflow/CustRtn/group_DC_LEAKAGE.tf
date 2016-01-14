hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "PinGroupList" = "LEAK_EVEN_1P8V_CLK_zz_fpc1_PM3,LEAK_EVEN_1P8V_CLK_zz_fpc1_PM3,LEAK_ODD_1P8V_2_zz_fpc1_PM3,LEAK_ODD_1P8V_2_zz_fpc1_PM3,LEAK_EVEN_1P8V_2_zz_fpc1_PM3,LEAK_EVEN_1P8V_2_zz_fpc1_PM3,LEAK_EVEN_1P8V_FREQ_zz_fpc1_PM3,LEAK_EVEN_1P8V_FREQ_zz_fpc1_PM3";
  "StopVector" = "0";
  "_sDisconectPinList" = "";
  "_sVForce_VList" = "1.89,0,1.89,0,1.89,0,1.89,0";
tm_2:
  "PinGroupList" = "LEAK_PU_1P8V_z_fpc1_pu";
  "StopVector" = "0";
  "_sDisconectPinList" = "";
  "_sVForce_VList" = "0";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.DC.DC_Leakage";
tm_2:
  testmethod_class = "ti_tml.DC.DC_Leakage";

end
-----------------------------------------------------------------
test_suites

DC_Leakage_zz_fpc1:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 7;
  override_levset = 2;
  override_testf = tm_1;
  override_tim_spec_set = "AC_per_33_12";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
DC_Leakage_zz_fpc1_pu:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 7;
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
    run_and_branch(DC_Leakage_zz_fpc1)
    then
    {
    }
    else
    {
    }
    run_and_branch(DC_Leakage_zz_fpc1_pu)
    then
    {
    }
    else
    {
    }

  },groupbypass, open,"DC_LEAKAGE",""

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
