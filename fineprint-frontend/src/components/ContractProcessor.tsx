"use client"

import { useState, useCallback } from "react"
import { UploadCloud, File, AlertCircle, CheckCircle2, AlertTriangle, ShieldAlert, FileText, Loader2, ArrowRight } from "lucide-react"

interface ComplianceCheck {
    clause_text: string
    is_compliant: boolean
    violation_reason: string | null
    regulatory_citation: string | null
    suggested_fix: string | null
}

interface AuditReportResponse {
    overall_compliance_score: number
    clauses_analyzed: number
    violations_found: number
    details: ComplianceCheck[]
}

export function ContractProcessor() {
    const [file, setFile] = useState<File | null>(null)
    const [isProcessing, setIsProcessing] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<AuditReportResponse | null>(null)
    const [isDragging, setIsDragging] = useState(false)

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setIsDragging(true)
        } else if (e.type === "dragleave") {
            setIsDragging(false)
        }
    }, [])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDragging(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0]
            if (droppedFile.type === "application/pdf") {
                setFile(droppedFile)
                setError(null)
            } else {
                setError("Please upload a purely PDF file.")
            }
        }
    }, [])

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
            setError(null)
        }
    }

    const processContract = async () => {
        if (!file) return

        setIsProcessing(true)
        setError(null)

        const formData = new FormData()
        formData.append("file", file)

        try {
            const response = await fetch("http://127.0.0.1:8000/upload-contract", {
                method: "POST",
                body: formData,
            })

            if (!response.ok) {
                throw new Error("Failed to process contract. Is the backend running?")
            }

            const data = await response.json()
            setResult(data)
        } catch (err: any) {
            setError(err.message || "An unexpected error occurred.")
        } finally {
            setIsProcessing(false)
        }
    }

    const handleExportPDF = () => {
        window.print()
    }

    return (
        <div className="w-full max-w-5xl mx-auto space-y-8">
            {/* Upload Section */}
            {!result && (
                <div
                    className={`relative overflow-hidden transition-all duration-300 rounded-3xl border-2 ${isDragging
                        ? "border-indigo-500 bg-indigo-50 shadow-xl scale-[1.02]"
                        : "border-dashed border-slate-300 bg-white hover:border-slate-400"
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div className="p-16 text-center">
                        {isProcessing ? (
                            <div className="flex flex-col items-center justify-center space-y-4 animate-pulse">
                                <Loader2 className="w-14 h-14 text-indigo-600 animate-spin" />
                                <h3 className="text-xl font-semibold text-slate-900">
                                    Auditing Regulatory Compliance...
                                </h3>
                                <p className="text-slate-500 max-w-md mx-auto">
                                    Our specialized Agent is scanning the clauses against RBI and Consumer Protection Guardrails. This takes about 15 seconds.
                                </p>
                            </div>
                        ) : file ? (
                            <div className="flex flex-col items-center justify-center space-y-6">
                                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center">
                                    <FileText className="w-10 h-10 text-emerald-600" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-semibold text-slate-900">
                                        {file.name}
                                    </h3>
                                    <p className="text-slate-500 mt-2">
                                        Document Ready. Click below to initiate the audit.
                                    </p>
                                </div>
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setFile(null)}
                                        className="px-6 py-3 rounded-xl border border-slate-200 text-slate-600 font-medium hover:bg-slate-50 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={processContract}
                                        className="px-8 py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
                                    >
                                        Initiate Audit
                                        <ShieldAlert className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center space-y-4">
                                <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                                    <UploadCloud className="w-12 h-12 text-slate-400" />
                                </div>
                                <h3 className="text-2xl font-bold text-slate-700">
                                    Upload Financial Contract
                                </h3>
                                <p className="text-slate-500 max-w-sm mx-auto">
                                    Drag and drop your PDF file here, or click the button below to
                                    browse your secure local files.
                                </p>
                                <label className="mt-8 inline-block cursor-pointer">
                                    <span className="px-8 py-3.5 rounded-full bg-slate-900 text-white font-semibold hover:bg-slate-800 transition-colors shadow-md">
                                        Select a PDF
                                    </span>
                                    <input
                                        type="file"
                                        className="hidden"
                                        accept=".pdf"
                                        onChange={handleFileInput}
                                    />
                                </label>
                            </div>
                        )}

                        {error && (
                            <div className="mt-8 p-4 bg-red-50 text-red-700 rounded-xl flex items-start gap-3 border border-red-100 text-left max-w-2xl mx-auto">
                                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h4 className="font-semibold">Audit Exception</h4>
                                    <p className="text-sm mt-1">{error}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Audit Results Dashboard View */}
            {result && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

                    {/* Top Summary Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200 flex flex-col justify-center items-center text-center">
                            <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Compliance Score</h4>
                            <div className="flex items-end gap-2 text-indigo-600">
                                <span className="text-5xl font-black">{result.overall_compliance_score}</span>
                                <span className="text-xl font-bold mb-1">/100</span>
                            </div>
                        </div>
                        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200 flex flex-col justify-center items-center text-center">
                            <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Clauses Analyzed</h4>
                            <div className="flex items-center gap-2 text-slate-800">
                                <FileText className="w-8 h-8 opacity-50" />
                                <span className="text-5xl font-black">{result.clauses_analyzed}</span>
                            </div>
                        </div>
                        <div className={`rounded-3xl p-6 shadow-sm border flex flex-col justify-center items-center text-center ${result.violations_found > 0 ? "bg-red-50 border-red-200 text-red-700" : "bg-emerald-50 border-emerald-200 text-emerald-700"}`}>
                            <h4 className={`text-sm font-bold uppercase tracking-wider mb-2 ${result.violations_found > 0 ? "text-red-500" : "text-emerald-500"}`}>Violations Found</h4>
                            <div className="flex items-center gap-2">
                                {result.violations_found > 0 ? <AlertTriangle className="w-8 h-8 opacity-80" /> : <CheckCircle2 className="w-8 h-8 opacity-80" />}
                                <span className="text-5xl font-black">{result.violations_found}</span>
                            </div>
                        </div>
                    </div>

                    {/* Action Header */}
                    <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                        <h2 className="text-2xl font-bold text-slate-900">Detailed Audit Log</h2>
                        <div className="flex gap-3">
                            <button
                                onClick={handleExportPDF}
                                className="text-sm font-semibold text-slate-700 hover:text-indigo-600 bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-sm hover:shadow transition-all"
                            >
                                Export Audit Report (PDF)
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null)
                                    setFile(null)
                                }}
                                className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl shadow-sm hover:shadow transition-all"
                            >
                                Scan Another Policy
                            </button>
                        </div>
                    </div>

                    {/* Clauses List */}
                    <div className="space-y-6">
                        {result.details.map((clause, idx) => (
                            <div key={idx} className={`flex flex-col gap-6 p-6 rounded-2xl border-l-4 shadow-sm bg-white ${clause.is_compliant ? "border-l-emerald-500 border-t border-r border-b border-slate-100" : "border-l-red-500 border-red-100 bg-red-50/10"}`}>

                                {/* Clause Header */}
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-2">
                                        {clause.is_compliant ? (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider">
                                                <CheckCircle2 className="w-3.5 h-3.5" /> Compliant
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-100 text-red-800 text-xs font-bold uppercase tracking-wider">
                                                <AlertCircle className="w-3.5 h-3.5" /> Violation
                                            </span>
                                        )}
                                        <span className="text-xs font-semibold text-slate-400">ID: CL-{String(idx + 1).padStart(3, '0')}</span>
                                    </div>
                                </div>

                                {/* Original Text */}
                                <div className="">
                                    <p className="text-base font-serif text-slate-800 leading-relaxed italic border-l-2 border-slate-200 pl-4 py-1">
                                        "{clause.clause_text}"
                                    </p>
                                </div>

                                {/* Violation Details (Only show if not compliant) */}
                                {!clause.is_compliant && (
                                    <div className="bg-white p-5 rounded-xl border border-red-200 shadow-sm space-y-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <h4 className="text-xs font-bold text-red-600 uppercase tracking-wider mb-1">Violation Reason</h4>
                                                <p className="text-sm font-medium text-slate-900">{clause.violation_reason}</p>
                                            </div>
                                            <div>
                                                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Regulatory Citation</h4>
                                                <p className="text-sm font-medium text-slate-700 flex items-start gap-1.5">
                                                    <FileText className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                                                    {clause.regulatory_citation}
                                                </p>
                                            </div>
                                        </div>
                                        {clause.suggested_fix && (
                                            <div className="pt-4 border-t border-red-100">
                                                <h4 className="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2">Suggested Compliant Revision</h4>
                                                <p className="text-sm font-medium text-emerald-900 bg-emerald-50 px-4 py-3 rounded-lg border border-emerald-100">
                                                    {clause.suggested_fix}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
