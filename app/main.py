from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, Field, field_validator

from typing import List, Literal, Optional, Dict, Any

from app.models.ctRSD_simulator_210 import RSD_sim, FILEPATH_DOMAINS
from app.models.process_workbook import process_workbook, compile_workbook_data

api = FastAPI()

class CompileRequest(BaseModel):
    name      : str = Field(..., description="Name of the sequence to compile")
    Rz        : str | None = Field('Ro', description="Ribozyme parameter")
    L         : str | None = Field('L', description="Ribozyme Linker parameter")
    term      : str | None = Field('T7t', description="Terminator parameter")
    hp5       : str | None = Field('5hp', description="Hairpin 5' parameter")
    prom      : str | None = Field('T7p', description="Promoter parameter")
    eI        : str | None = Field('', description="eI parameter")
    eO        : str | None = Field('', description="eO parameter")
    s         : str | None = Field('', description="s parameter")
    invert    : int | None = Field(0, description="invert parameter")
    invL      : str | None = Field('A', description="invL parameter")
    agL       : str | None = Field('TA', description="agL parameter")
    AGiloop   : int | None = Field(5, description="AGiloop parameter")
    otype     : int | None = Field(1, description="otype parameter")
    rna       : int | None = Field(0, description="rna parameter")
    us        : List[Any] | None = Field([], description="us parameter")
    ds        : List[Any] | None = Field([], description="ds parameter")
    temp_len  : int | None = Field(0, description="temp_len parameter")
    cp        : str | None = Field('', description="cp parameter")
    n         : str | None = Field('', description="n parameter")
    c         : int | None = Field(0, description="c parameter")
    d         : str | None = Field('', description="d parameter")
    CDS       : str | None = Field('', description="CDS parameter")
    rflap     : str | None = Field('', description="rflap parameter")

    @field_validator('Rz', 'L', 'term', 'hp5', 'prom', 'eI', 'eO', 's', 'invL', 'agL', 'cp', 'n', 'd', 'CDS', 'rflap', mode='before')
    @classmethod
    def _none_to_default(cls, v, info):
        return cls.model_fields[info.field_name].default if v is None else v

class CompileResponse(BaseModel):
    dna_template: str = Field(..., description="DNA template sequence")
    rna_template: str = Field(..., description="RNA template sequence")
    dna_part_IDs: List[str] = Field(..., description="List of DNA part IDs")
    rna_part_IDs: List[str] = Field(..., description="List of RNA part IDs")
    dna_part_types: List[str] = Field(..., description="List of DNA part types")
    rna_part_types: List[str] = Field(..., description="List of RNA part types")
    dna_part_orientations: List[str] = Field(..., description="List of DNA part orientations")
    rna_part_orientations: List[str] = Field(..., description="List of RNA part orientations")
    genbank_dna: str | None = Field(..., description="GenBank DNA file content")
    genbank_rna: str | None = Field(..., description="GenBank RNA file content")

@api.post('/compile')
def compile(request: CompileRequest):
    model = RSD_sim()
    model.load_domains(FILEPATH_DOMAINS)

    print("Compiling sequence with the following parameters:", request.dict())
    result = model.ctRSD_seq_compile(
        name = request.name,
        Rz = request.Rz,
        L = request.L,
        term = request.term,
        hp5 = request.hp5,
        prom = request.prom,
        eI = request.eI,
        eO = request.eO,
        s = request.s,
        invert = request.invert,
        invL = request.invL,
        agL = request.agL,
        AGiloop = request.AGiloop,
        otype = request.otype,
        rna = request.rna,
        us = request.us,
        ds = request.ds,
        temp_len = request.temp_len,
        cp = request.cp,
        n = request.n,
        c = request.c,
        d = request.d,
        CDS = request.CDS,
        rflap = request.rflap
    )
    #print("Compilation result:", result)

    return CompileResponse(
        dna_template=result[0],
        rna_template=result[1],
        dna_part_IDs=result[2],
        rna_part_IDs=result[3],
        dna_part_types=result[4],
        rna_part_types=result[5],
        dna_part_orientations=result[6],
        rna_part_orientations=result[7],
        genbank_dna=result[8],
        genbank_rna=result[9]
    )


class CompileExcelResponse(BaseModel):
    name: List[List[str]] = Field(..., description="List of names for each row and sheet")
    dna_template: List[List[str]] = Field(..., description="DNA template sequence")
    rna_template: List[List[str]] = Field(..., description="RNA template sequence")
    dna_part_IDs: List[List[List[str]]] = Field(..., description="List of DNA part IDs")
    rna_part_IDs: List[List[List[str]]] = Field(..., description="List of RNA part IDs")
    dna_part_types: List[List[List[str]]] = Field(..., description="List of DNA part types")
    rna_part_types: List[List[List[str]]] = Field(..., description="List of RNA part types")
    dna_part_orientations: List[List[List[str]]] = Field(..., description="List of DNA part orientations")
    rna_part_orientations: List[List[List[str]]] = Field(..., description="List of RNA part orientations")
    genbank_dna: List[List[str]] | None = Field(..., description="GenBank DNA file content")
    genbank_rna: List[List[str]] | None = Field(..., description="GenBank RNA file content")
    unique_parts: List[Dict[str, str]] = Field(..., description="List of unique RNA parts with their types")

@api.post('/compile/excel')
def compile_workbook(workbook: UploadFile = File(...), get_genbank: int = 0):
    if not workbook.filename:
        raise HTTPException(400, "Workbook filename is missing")
    
    if not workbook.filename.lower().endswith(".xlsx"):
        raise HTTPException(400, "Expected an .xlsx workbook")
    
    # Process the workbook file here
    data, num_rows = process_workbook(workbook)

    # Compile 
    results = compile_workbook_data(data, num_rows, get_genbank=get_genbank)

    print("Compilation results:", results.keys())
    #print("\n\nUnique parts:", results['unique_parts'])
    print("\n\nNumber of unique parts:", len(results['unique_parts']))
    return CompileExcelResponse(
        name=results['name'],
        dna_template=results['dna_template'],
        rna_template=results['rna_template'],
        dna_part_IDs=results['dna_part_IDs'],
        rna_part_IDs=results['rna_part_IDs'],
        dna_part_types=results['dna_part_types'],
        rna_part_types=results['rna_part_types'],
        dna_part_orientations=results['dna_part_orientations'],
        rna_part_orientations=results['rna_part_orientations'],
        genbank_dna=results['genbank_dna'],
        genbank_rna=results['genbank_rna'],
        unique_parts=results['unique_parts']
    )

@api.get('/domains')
def get_domains():
    try:
        model = RSD_sim()
        model.load_domains(FILEPATH_DOMAINS)
        #return JSONResponse(content=jsonable_encoder({"domains": model.domains}))
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": "Internal server error occurred"}), status_code=500)


@api.get('/hello')
def hello():
    try:
        return JSONResponse(content=jsonable_encoder({"message": "Hello, world!"}))
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": "Internal server error occurred"}), status_code=500)


if __name__ == '__main__':
    uvicorn.run(api, host="0.0.0.0", port=8010, log_level="info")