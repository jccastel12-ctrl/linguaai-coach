import { NextResponse } from "next/server";
import { backendFetch, readApiError } from "@/lib/server-auth";
export async function POST(request:Request){const body=await request.text();const response=await backendFetch("/api/v1/auth/email-verification/confirm",{method:"POST",body});if(!response.ok)return NextResponse.json({detail:await readApiError(response)},{status:response.status});return NextResponse.json(await response.json());}
