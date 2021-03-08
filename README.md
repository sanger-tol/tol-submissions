# submissions

Submit ToL data to EMBL-EBI ENA & BioSamples


Notes:

INITIAL SETUP:
Copy *all* of the COPO development branch into the COPO folder. https://github.com/collaborative-open-plant-omics/COPO 
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt 

Copy DToL classes into ToL classes, just to keep our hacking different
    cp submissions/COPO/web/apps/web_copo/utils/dtol/*.py .
    mv Dtol_Helpers.py Tol_Helpers.py
    mv Dtol_Spreadsheet.py Tol_Spreadsheet.py
    mv Dtol_Submission.py Tol_Submission.py


Change COPO relative paths in the python classes. Example
from:
    import web.apps.web_copo.schemas.utils.data_utils as d_utils
    from api.utils import map_to_dict

To:
    import COPO.web.apps.web_copo.schemas.utils.data_utils as d_utils
    from COPO.api.utils import map_to_dict


CLARIFICATION:
Q: Ken Haug. I am puzzled by the order of ENA vs BioSamples, but the code is making this more clear. Yes, I will map this against a spreadsheet or database.  Do I need separate ENA (Webin) and BioSamples accounts, I assume not.
A: alice minotto. We only submit to ENA, they return both their accession and the biosample accession (so the biosample is created automatically by submitting to ENA), plus a "submission accession", which is a single accession code for the whole submission so if you are submitting 200 samples all together, you would only get one submission accession


WEBIN account:
Your new submission account has been created. The submission account id is Webin-58409. Email: tol-platforms@sanger.ac.uk
For submission guidelines please see: https://urldefense.proofpoint.com/v2/url?u=http-3A__ena-2Ddocs.readthedocs.io_en_latest_index.html&d=DwICAg&c=D7ByGjS34AllFgecYw0iC6Zq7qlm8uclZFI0SqQnqBo&r=niIFX4ijhZ7nQFbTJqwQSb5VItoTCmHYLVHPara9N14&m=dI4cdozOXMtg-MjiEeV7rpS3AGuQevHXdw8JGzbbbts&s=V36t4ufpn5OtbKnCRtoAcSpGtO7gE6VqsjIOiaQgrFY&e= 



ToDo list:
- Change from mongo db to database orm/spreadsheet
- Change project from DTOL/ASG to TOL
- Test that we can submit to the ENA DTOL profile
