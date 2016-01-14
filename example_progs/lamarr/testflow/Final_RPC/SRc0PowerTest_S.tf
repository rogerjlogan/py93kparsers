hp93000,testflow,0.1
language_revision = 1;

testmethodparameters

tm_1:
  "VDDCORE_Spec" = "VDDCORE_PS";
  "Vmax.Vmax1_Sets" = "";
  "Vmax.Vmax2_Sets" = "";
  "Vmax.Vmax3_Sets" = "";
  "Vmax.suite" = "";
  "Vmin.Vmin1_Sets" = "SRVminOD,SRVminDDR3L";
  "Vmin.Vmin2_Sets" = "";
  "Vmin.Vmin3_Sets" = "";
  "Vmin.suite" = "IddqVmin1_IqC08Ful_______LM10_005_st_PM1_MEAS";
  "Vnom.Vnom1_Sets" = "";
  "Vnom.Vnom2_Sets" = "";
  "Vnom.Vnom3_Sets" = "";
  "Vnom.suite" = "IddqVnom_IqC08Ful_______LM10_005_st_PM1_MEAS";

end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
testmethods

tm_1:
  testmethod_class = "ti_tml.SmartReflex.SR_SRc0PowerTest";

end
-----------------------------------------------------------------
test_suites

SRc0PowerTest:
  local_flags = output_on_pass, output_on_fail, value_on_pass, value_on_fail, per_pin_on_pass, per_pin_on_fail;
  override = 1;
  override_lev_equ_set = 1;
  override_lev_spec_set = 4;
  override_levset = 2;
  override_testf = tm_1;
  override_tim_spec_set = "efuse_Read_Program";
  override_timset = "1,1,1";
  site_control = "parallel:";
  site_match = 2;

end
-----------------------------------------------------------------
test_flow

  {
    if @TITESTTYPE != "PB_RPC_LT" then
    {
       if @TMLimit_TestMode == "TEMP_ROOM_DEG" then
       {
          print("Skipping Src0PowerTest since ROOM or COLD TEMP");
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

  },open,"SRc0PowerTest_S",""

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
