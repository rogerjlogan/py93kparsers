hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "IForce1_mA" = "-14";
  "IForce2_mA" = "-24";
  "PinList" = "CRES_PINS1";
  "VClamp_V" = "-2";

end
-----------------------------------------------------------------
testmethodlimits


end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "miscellaneous_tml.TestControl.Disconnect";
tm_2:
  testmethod_class = "ti_tml.DC.Cres";

end
-----------------------------------------------------------------
test_suites

DISCONNECT_Cres:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;
Cres_st:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 1;
  override_levset = 1;
  override_seqlbl = "";
  override_testf = tm_2;
  override_tim_equ_set = 1;
  override_tim_spec_set = 1;
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow
  {
    run(DISCONNECT_Cres);
    run_and_branch(Cres_st)
    then
    {
    }
    else
    {
    }
  },open,"CRES_S",""

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
