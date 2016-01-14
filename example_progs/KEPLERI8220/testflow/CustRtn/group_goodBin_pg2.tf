hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "CRES TestSuite Name" = "";
  "Categories Binning" = "YES";
  "IForce1_mA" = "0";
  "IForce2_mA" = "0";
  "Is it the Final End of Flow Binning?" = "NO";
  "Partial Binning" = "NO";
  "PinList" = "";
  "Run CRES" = "NO";
  "Special Bin Disconnect" = "NO";
  "VClamp_V" = "0";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.Misc.Binning";

end
-----------------------------------------------------------------
test_suites

DISCONNECT_AtEndOfFlow:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
Final_Binning:
  comment = "Final Binning based on Categories and Groups";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 8;
  override_levset = 2;
  override_seqlbl = "PB_PLL_S1R_T0_1_PG_ASV_MPB";
  override_testf = tm_2;
  override_tim_spec_set = "PBIST_pASYNC2_pASYNC3_pNONASYNC1_WFT11X4_MPT_1214";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(DISCONNECT_AtEndOfFlow);
    run_and_branch(Final_Binning)
    then
    {
    }
    else
    {
       multi_bin;
    }

  },open,"group_goodBin",""

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
