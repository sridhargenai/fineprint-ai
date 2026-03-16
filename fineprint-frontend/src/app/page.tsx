import Image from "next/image";
import { ContractProcessor } from "@/components/ContractProcessor";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-[family-name:var(--font-geist-sans)]">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">F</span>
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-600 to-indigo-600">
                FinePrint AI
              </span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-6 flex flex-col gap-2">
            <span>Automate your compliance.</span>
            <span className="text-indigo-600">Audit instantly.</span>
          </h1>
          <p className="text-lg text-slate-600 mb-8">
            Upload loan agreements and financial contracts. Our AI Auditor instantly scans clauses against current RBI and Consumer Protection guardrails, flagging regulatory risks and suggesting compliant alternatives before you sign or disburse.
          </p>
        </div>

        {/* Interactive File Uploader & Results */}
        <div className="mt-8 flex justify-center">
          <ContractProcessor />
        </div>

      </main>
    </div>
  );
}
