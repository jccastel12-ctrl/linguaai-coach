import { NextResponse } from "next/server";
import { backendFetch, readApiError } from "@/lib/server-auth";
export async function POST(request:Request){const body=await request.text();try{const response=await backendFetch("/api/v1/auth/password-reset/request",{method:"POST",body});if(!response.ok)return NextResponse.json({detail:await readApiError(response)},{status:response.status});return NextResponse.json(await response.json(),{status:202});}catch{return NextResponse.json({message:"Si la cuenta existe, recibirás instrucciones."},{status:202});}}
