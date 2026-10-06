# Sample demo data (synthetic)

These files simulate the messy, scattered source documents a typical SME
finance team would upload: a power bill, a gas bill, fuel logs, a flight
itinerary CSV, a waste memo and a commute survey.

All data is **synthetic** and written for the GreenLedger demo
(GreenLeaf Trading Co. is a fictional company). Figures are internally
consistent and expressed in the units of the bundled emission-factor library
(kWh, m3, liter, passenger-km, tonne, km, night) so the mock pipeline and the
Gemini pipeline both produce complete, verifiable results.

Two extra files are tiny synthetic **PDFs** of the electricity and gas bills
(`electricity_bill_June2025.pdf`, `natural_gas_bill_June2025.pdf`, ~1–2 KB each).
Regenerate with `python sample_data/make_sample_pdfs.py`.
**Load sample company** still uses the six **txt/csv** files so mock totals stay
stable. For a Gemini multimodal take, upload the two PDFs **instead of** the
matching `.txt` bills (do not upload both or quantities will double-count).

Keep the `.txt` twins in the folder as the text source of truth for the generator.
