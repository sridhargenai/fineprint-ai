import fitz

doc = fitz.open()
page = doc.new_page()

text = """
LOAN AGREEMENT
--------------------------------------------------

This Loan Agreement ("Agreement") is entered into today between the Lender 
and the Borrower.

Clause 1: 
The Lender reserves the right to charge an interest rate that may vary at the 
Lender's sole discretion, without prior notice or disclosure of the full repayment 
schedule.

Clause 2: 
If the Borrower is late on any payment, an immediate penalty charge of 25% 
of the total loan value will be applied automatically. This fee is non-refundable.

Clause 3: 
The Lender may deduct a hidden processing fee directly from the principal 
before disbursement, which the borrower cannot contest.

Clause 4: 
Any disputes arising from this Agreement shall be resolved through binding 
arbitration. The arbitrator will be chosen solely by the Lender.

Clause 5: 
The borrower agrees to a standard loan term of 12 months, which is fully 
compliant.
"""

# Insert text
page.insert_text((50, 72), text, fontname="helv", fontsize=12)

doc.save("Hackathon_Demo_Contract.pdf")
print("Successfully generated Hackathon_Demo_Contract.pdf")
