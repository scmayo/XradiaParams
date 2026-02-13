# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 15:51:08 2026

@author: may130 - Heavily modified from Yakov's code'
"""
#This file contain tools for extracting metadata from a TXRM file which is an OLE format file of tomography scan data produced by Xradia Tomography instruments

#The five functions below are helper functions for extracting data from ole streams in various formats

def GetFloatAttr(ole, string: str):
    if ole.exists(string):    
        objtype = ole.get_type(string)
        if objtype is olefile.STGTY_STREAM:
            stream = ole.openstream(string)
            data = stream.read()
            return np.frombuffer(data, dtype=np.float32)
    else:
        return np.array([])

def GetIntAttr(ole, string: str):
    if ole.exists(string):    
        objtype = ole.get_type(string)
        if objtype is olefile.STGTY_STREAM:
            stream = ole.openstream(string)
            data = stream.read()
            return np.frombuffer(data, dtype=np.int32)
    else:
        return np.array([])

def GetFloatImage(ole, string: str, shape):
    if ole.exists(string):    
        objtype = ole.get_type(string)
        if objtype is olefile.STGTY_STREAM:
            stream = ole.openstream(string)
            return np.ndarray(shape, dtype = np.float32, buffer = stream.read(), order = 'C')
    else:
        return np.array([])

def GetText(ole, string: str):
    if ole.exists(string):
        objtype = ole.get_type(string)
        if objtype is olefile.STGTY_STREAM:
            stream = ole.openstream(string)
            data = stream.read()
            return (data.split(b"\0", 1)[0])
    else:
        return np.array([])

def GetDate(ole, string: str):
    if ole.exists(string):
        objtype = ole.get_type(string)
        if objtype is olefile.STGTY_STREAM:
            stream = ole.openstream(string)
            data = stream.read()
            foo = data.split(b"\0")
            bar = [i for i in foo if len(i)>2]
            return ((bar[0]).split(b".")[0],bar[-1].split(b".")[0])
    else:
        return np.array([])

def SampleParams(strFile: str, Sampleno: str, Altime: int = 15, Proctime: int = 15):
    #This function extracts the desired subset of the metadata from a TXRM file using the olefile tools and 
    #returns them in a formatted form as "output" them along with a summary of the output "feedback" for
    #sending to console or a GUI
    
    if strFile == "":
        print("Missing filename! Terminating...")
        return None
        
    outstring = ""
    data = ""
    feedback = ""
    
    from pathlib import Path
    my_file = Path(strFile)

    if not my_file.is_file():
        feedback+=("File does not exist! Terminating...")
        return None,feedback

    if (str(Path(strFile).suffix) != ".txrm"):
        feedback+=("File not a .txrm file! Terminating...")
        return None,feedback


    if olefile.isOleFile(strFile):
        with olefile.OleFileIO(strFile, write_mode=True) as ole:
            #feedback+=("Opening file...")
            
            # Extract required parameters
            Voltage = GetFloatAttr(ole, 'ImageInfo/Voltage')
            if len(Voltage) == 0:
                print('Could not find voltage. Terminating...')
                return None,feedback
            feedback+=(f'\nVoltage: {Voltage[0]} kV')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Voltage,"+f"{Voltage[0]:.0f}\n")

            Power = GetFloatAttr(ole, 'AcquisitionSettings/SrcPower')
            if len(Power) == 0:
                feedback+=('Could not find Power. Terminating...')
                return None,feedback
            feedback+=(f'\nPower: {Power[0]} W')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Power,"+f"{Power[0]:.0f}\n")

            Filter = GetText(ole, 'AcquisitionSettings/SourceFilterName')
            if len(Filter) == 0:
                feedback+=('Could not find Filter. Terminating...')
                return None,feedback
            feedback+=("\nFilter: "+Filter.decode('ascii'))
            data = Filter.decode('ascii')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Source Filter,"+data+"\n")

            FramesPerImage = GetIntAttr(ole, 'AcquisitionSettings/FramesPerImage')
            if len(FramesPerImage) == 0:
                feedback+=('Could not find FramesPerImage. Terminating...')
                return None,feedback
            feedback+=(f'\nFrames per Image: {FramesPerImage[0]:.0f}')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Frames per image,"+f"{FramesPerImage[0]:.0f}\n")
            
            
            ExpTime = GetFloatAttr(ole, 'AcquisitionSettings/ExpTime')
            if len(ExpTime) == 0:
                feedback+=('Could not find ExpTime. Terminating...')
                return None,feedback
            feedback+=(f'\nExp Time: {ExpTime[0]:.1f} mm')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Exposure time,"+f"{ExpTime[0]:.1f}\n")
            
            ObjName = GetText(ole, 'ImageInfo/ObjectiveName')
            if len(ObjName) == 0:
                feedback+=('Could not find ObjName. Terminating...')
                return None,feedback
            feedback+=("\nDetector:"+ObjName.decode('ascii'))
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Objective,"+ObjName.decode('ascii')+"\n")

            Binning = GetIntAttr(ole, 'AcquisitionSettings/Binning')
            if len(Binning) == 0:
                feedback+=('Could not find Binning. Terminating...')
                return None,feedback
            feedback+=(f'\nBinning: {Binning[0]:.0f}')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Binning,"+f"{Binning[0]:.0f}\n")
            
            NumStitch = GetIntAttr(ole, 'AcquisitionSettings/StitchParams/AutoStitchSettings/NumSegments')
            if len(NumStitch) == 0:
                feedback+=('\nCould not find NumStitch - stitch = 1.')
                outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Number of stitches,1\n")

            else:
                feedback+=(f'\nNumStitch: {NumStitch[0]}')
                outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Number of stitches,"+f"{NumStitch[0]:.0f}\n")
            
            NumImages = GetIntAttr(ole, 'ImageInfo/NoOfImages')
            if len(NumImages) == 0:
                feedback+=('Could not find Num Images. Terminating...')
                return None,feedback
            feedback+=(f'\nNum Images: {NumImages[0]}')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Projections,"+f"{NumImages[0]:.0f}\n")
            
            PixSize = GetFloatAttr(ole, 'ImageInfo/PixelSize')
            if len(PixSize) == 0:
                feedback+=('Could not find PixelSize. Terminating...')
                return None,feedback
            feedback+=(f'\nPix Size: {PixSize[0]:.2f} um')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Pixel Size,"+f"{PixSize[0]:.2f}\n")

            DateTime = GetDate(ole, 'ImageInfo/Date')
            if len(DateTime) == 0:
                feedback+=('Could not find DateTime. Terminating...')
                return None,feedback
            feedback+=("\nStart, end time:"+DateTime[0].decode('ascii')+DateTime[1].decode('ascii'))
            format_string = "%m/%d/%Y %H:%M:%S"
            t1= datetime.strptime(DateTime[0].decode('ascii'), format_string)
            t2 = datetime.strptime(DateTime[1].decode('ascii'), format_string)
            seconds_diff = t2.timestamp() - t1.timestamp()
            outstring+=("0,"+Sampleno+f",Global,Scanning Parameters,Scan Time,{(seconds_diff/3600):.2f}\n")

            outstring+=("0,"+Sampleno+f",Global,Scanning Parameters,Alignment time,{Altime:.0f}\n")

            BHparam = GetFloatAttr(ole, 'ReconSettings/BeamHardening')
            if len(BHparam) == 0:
                feedback+=('Could not find BHparam. Terminating...')
                return None,feedback
            feedback+=(f'\nBH param: {BHparam[0]:.2f} um')
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,Beam Hardening,"+f"{BHparam[0]:.2f}\n")

            VLTmode = GetText(ole, 'ReconSettings/BeamHardeningFileName')
            if len(VLTmode) == 0:
                feedback+=('\nCould not find VLTmode. Terminating...')
                return None,feedback
            temp = VLTmode.decode('ascii')
            feedback+=("\nVLTmode:"+temp)
            vltyes = "FALSE"
            if (temp == "BH Correction for Very Low Transmission"):
                vltyes="TRUE"
            outstring+=("0,"+Sampleno+",Global,Scanning Parameters,VLT Correction,"+vltyes+"\n")

            outstring+=("0,"+Sampleno+f",Global,Scanning Parameters,Processing Time,{Proctime:.0f}\n")

            
        #print(outstring)
        
    else:
        feedback+=("Unsupported file format. Terminating...")
    return outstring,feedback

def MakeTable(strFile: str, SampleNos, Altime: int = 15, Proctime: int = 15):
    #This function creates a formatted list of (the same) metadata for multiple samples suitable for importing into our LIMS
    
    outtable = ",Sample ID,Phase,Analysis,Component Name,Value\n"
    params, feedback = SampleParams(strFile,"0000", Altime, Proctime)
    if params == None:
        return None, feedback
    for i in SampleNos:
        outtable+=params.replace("0000",str(i))        
    return outtable,feedback
