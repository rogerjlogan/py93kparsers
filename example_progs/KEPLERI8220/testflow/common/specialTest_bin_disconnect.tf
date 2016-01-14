hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "CRES TestSuite Name" = "";
  "Categories Binning" = "YES";
  "IForce1_mA" = "0";
  "IForce2_mA" = "0";
  "Is it the Final End of Flow Binning?" = "YES";
  "Partial Binning" = "NO";
  "PinList" = "";
  "Run CRES" = "NO";
  "Special Bin Disconnect" = "YES";
  "VClamp_V" = "0";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.Misc.Binning";

end
-----------------------------------------------------------------
bin_disconnect
  comment = "Time stamp and CTCS control";
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow


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
