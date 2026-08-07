from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

from app.models.ctRSD_simulator_210 import RSD_sim, FILEPATH_DOMAINS

api = FastAPI()

class CompileRequest(BaseModel):
    name: str = Field(..., description="Name of the sequence to compile")
    Rz: str = Field('Ro', description="Ribozyme parameter")
    L: str = Field('L', description="Ribozyme Linker parameter")
    term: str = Field('T7t', description="Terminator parameter")
    hp5: str = Field('5hp', description="Hairpin 5' parameter")
    prom: str = Field('T7p', description="Promoter parameter")
    eI: str = Field('', description="eI parameter")
    eO: str = Field('', description="eO parameter")
    s: str = Field('', description="s parameter")
    invert: int = Field(0, description="invert parameter")
    invL: str = Field('A', description="invL parameter")
    agL: str = Field('TA', description="agL parameter")
    AGiloop: int = Field(5, description="AGiloop parameter")
    otype: int = Field(1, description="otype parameter")
    rna: int = Field(0, description="rna parameter")
    us: List[Any] = Field([], description="us parameter")
    ds: List[Any] = Field([], description="ds parameter")
    temp_len: int = Field(0, description="temp_len parameter")
    cp: str = Field('', description="cp parameter")
    n: str = Field('', description="n parameter")
    c: int = Field(0, description="c parameter")
    d: str = Field('', description="d parameter")
    CDS: str = Field('', description="CDS parameter")
    rflap: str = Field('', description="rflap parameter")

class CompileResponse(BaseModel):
    dna_template: str = Field(..., description="DNA template sequence")
    rna_template: str = Field(..., description="RNA template sequence")
    dna_part_IDs: List[str] = Field(..., description="List of DNA part IDs")
    rna_part_IDs: List[str] = Field(..., description="List of RNA part IDs")
    dna_part_types: List[str] = Field(..., description="List of DNA part types")
    rna_part_types: List[str] = Field(..., description="List of RNA part types")
    genbank_dna: str = Field(..., description="GenBank DNA file content")
    genbank_rna: str = Field(..., description="GenBank RNA file content")

@api.post('/compile')
def compile(request: CompileRequest):
    model = RSD_sim()
    result = model.ctRSD_seq_compile(
        name = request.name,
        filepath = FILEPATH_DOMAINS,
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

    return CompileResponse(
        dna_template=result[0],
        rna_template=result[1],
        dna_part_IDs=result[2],
        rna_part_IDs=result[3],
        dna_part_types=result[4],
        rna_part_types=result[5],
        genbank_dna=result[6],
        genbank_rna=result[7]
    )


@api.get('/hello')
def hello():
    try:
        return JSONResponse(content=jsonable_encoder({"message": "Hello, world!"}))
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": "Internal server error occurred"}), status_code=500)


if __name__ == '__main__':
    uvicorn.run(api, host="0.0.0.0", port=7000, log_level="info")