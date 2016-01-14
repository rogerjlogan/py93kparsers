hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_2:
  "DoVcntlVerify" = "FALSE";
  "VDDCORE_Spec" = "VDDCORE_PS";
  "Vmax.Vmax1_Sets" = "";
  "Vmax.Vmax2_Sets" = "";
  "Vmax.Vmax3_Sets" = "";
  "Vmin.Vmin1_Sets" = "";
  "Vmin.Vmin2_Sets" = "SRVmin,SRVminDDR3L,VminVSROtlr";
  "Vmin.Vmin3_Sets" = "";
  "Vnom.Vnom1_Sets" = "";
  "Vnom.Vnom2_Sets" = "";
  "Vnom.Vnom3_Sets" = "";
  "isSOCSRc0" = "TRUE";
tm_3:
  "VDDCORE_Spec" = "VDDCORE_PS";
  "Vmax.Vmax1_Sets" = "";
  "Vmax.Vmax2_Sets" = "";
  "Vmax.Vmax3_Sets" = "";
  "Vmin.Vmin1_Sets" = "";
  "Vmin.Vmin2_Sets" = "SRVmin,SRVminDDR3L,VminVSROtlr";
  "Vmin.Vmin3_Sets" = "";
  "Vnom.Vnom1_Sets" = "";
  "Vnom.Vnom2_Sets" = "";
  "Vnom.Vnom3_Sets" = "";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.MCP.MCP_ReadVIDSpeeds";
tm_2:
  testmethod_class = "ti_tml.SmartReflex.SR_PreReadSRc0";
tm_3:
  testmethod_class = "ti_tml.SmartReflex.SR_setGlobalSRVoltage";

end
-----------------------------------------------------------------
test_suites

PreReadSrc0:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_testf = tm_2;
  override_tim_spec_set = "AC_per_10";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
ReadVIDSpeeds:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_testf = tm_1;
  override_tim_spec_set = "AC_per_10";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;
SetGlobalSRVoltages:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 10;
  override_levset = 2;
  override_testf = tm_3;
  override_tim_spec_set = "AC_per_10";
  override_timset = 1;
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    run(ReadVIDSpeeds);
    if @TITESTTYPE == "CUSTOMERRETURN" then
    {
       run(PreReadSrc0);
    }
    else
    {
    }
    if @TITESTTYPE == "PB_RPC_LT" then
    {
       run_and_branch(SetGlobalSRVoltages)
       then
       {
       }
       else
       {
          multi_bin;
       }
    }
    else
    {
    }

  },open,"PreReadSR_S",""

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
