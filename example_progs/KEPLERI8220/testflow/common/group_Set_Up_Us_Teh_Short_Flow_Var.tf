hp93000,testflow,0.1
language_revision = 1;

testmethodparameters
end
-----------------------------------------------------------------
testmethodlimits
end
-----------------------------------------------------------------
test_flow

  {
    if @TITESTTYPE != "FT_RPC_HT" then
    {
       @thisIsTehShortFlowz = 0;
       @thisIsPG2FT1 = 0;
    }
    else
    {
       if @TIDESIGNREV != "A" then
       {
          @thisIsTehShortFlowz = 0;
          @thisIsPG2FT1 = 1;
       }
       else
       {
          @thisIsTehShortFlowz = 1;
       }
    }

  },open,"Set_Up_Us_Teh_Short_Flow_Var",""

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
