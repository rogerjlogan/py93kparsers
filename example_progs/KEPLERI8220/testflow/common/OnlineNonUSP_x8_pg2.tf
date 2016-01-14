hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "enableSmartReflex" = "YES";
  "globalSROPPMode" = "2";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "USP_TM_Interface.USPSharedMemory.setUserVars";
tm_2:
  testmethod_class = "ti_tml.Misc.Init_Library";
tm_3:
  testmethod_class = "ti_tml.Misc.UpdateGuardBandSpecs";

end
-----------------------------------------------------------------
test_suites

Init_framework:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_2;
  site_control = "parallel:";
  site_match = 0;
UpdateGuardBand:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_testf = tm_3;
  site_control = "parallel:";
  site_match = 2;
setUserVars:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_test_number = 1;
  override_testf = tm_1;
  site_control = "parallel:";

end
-----------------------------------------------------------------
test_flow

  {
    run(setUserVars);
    if @TITESTTYPE == "Not_Defined" then
    {
       @USP_BRCONTROL = "main";
       @TILOADBOARD = "6576908B_W140610";
       @TITESTTYPE = "PB_RPC_HT";
       @TITESTTEMP = "TEMP_100_DEG";
       @TIDEVICETYPE = "RPC_SQ_SS";
       @TIROMCODE = "1";
       @TIDESIGNREV = "Z";
       @TIFABSITE = "FS_TSMC15";
       @TIFABCODE = "T";
    }
    else
    {
    }
    @TMLimit_TestMode = "@TITESTTEMP";
    run_and_branch(Init_framework)
    then
    {
    }
    else
    {
    }
    run(UpdateGuardBand);

  },open,"OnlineNonUSP",""

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
