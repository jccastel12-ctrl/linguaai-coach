import { NextResponse } from "next/server";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";
export async function POST(){const token=await getSessionToken();if(!token)return NextResponse.json({detail:"No autenticado."},{status:401});const response=await backendFetch("/api/v1/auth/email-verification/request",{method:"POST"},token);if(!response.ok)return NextResponse.json({detail:await readApiError(response)},{status:response.status});return NextResponse.json(await response.json());}
