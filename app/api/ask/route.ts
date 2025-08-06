import { type NextRequest, NextResponse } from "next/server"

interface ChatRequest {
  message: string
  language: "en" | "ak"
  history: Array<{
    content: string
    sender: "user" | "assistant"
    language: "en" | "ak"
  }>
}

// Mock health responses for demonstration
const healthResponses = {
  en: {
    greeting:
      "Hello! I'm here to help with your health questions. Please remember that I provide general information and you should consult a healthcare professional for serious concerns.",
    headache:
      "For headaches, try resting in a quiet, dark room, staying hydrated, and applying a cold or warm compress. If headaches persist or are severe, please consult a doctor.",
    fever:
      "For fever, rest, drink plenty of fluids, and consider over-the-counter fever reducers if appropriate. Seek medical attention if fever is high (over 103°F/39.4°C) or persists.",
    cough:
      "For coughs, try honey, warm liquids, and throat lozenges. If the cough persists for more than 2 weeks or is accompanied by blood, see a healthcare provider.",
    default:
      "I understand your concern. For specific medical advice, I recommend consulting with a healthcare professional who can properly assess your situation.",
  },
  ak: {
    greeting:
      "Akwaaba! Me wɔ ha sɛ meboa wo wɔ wo apɔmuden ho nsɛm mu. Kae sɛ mema wo amoa kɛse na ɛsɛ sɛ wo ne oduruyɛfoɔ kasa wɔ nsɛm a ɛho hia ho.",
    headache:
      "Sɛ wo ti yare a, home wɔ komm ne sum beae, nom nsuo pii, na fa nsuonwini anaa hyew nneɛma to wo ti so. Sɛ ti yare no kɔ so anaa ɛyɛ den a, kɔ oduruyɛfoɔ nkyɛn.",
    fever:
      "Sɛ wo ho hyew a, home, nom nsuo pii, na sɛ ɛho hia a, nom nnuro a ɛtumi te ɔhyew so. Sɛ ɔhyew no yɛ kɛse (ɛboro 103°F/39.4°C) anaa ɛkɔ so a, kɔ ayaresabea.",
    cough:
      "Sɛ wo wa a, sɔ ɛwo, nom nsuonwini nneɛma, na de menewa yɛ wo mene mu. Sɛ ɔwa no kɔ so nnawɔtwe mmienu anaa mogya ba mu a, kɔ oduruyɛfoɔ nkyɛn.",
    default:
      "Mete wo haw ase. Sɛ wopɛ oduruyɛfoɔ afotuo pɔtee a, mekamfo sɛ wo ne oduruyɛfoɔ bɛkasa na ɔahwɛ wo tebea yiye.",
  },
}

function getHealthResponse(message: string, language: "en" | "ak"): string {
  const lowerMessage = message.toLowerCase()
  const responses = healthResponses[language]

  if (lowerMessage.includes("hello") || lowerMessage.includes("hi") || lowerMessage.includes("akwaaba")) {
    return responses.greeting
  }

  if (lowerMessage.includes("headache") || lowerMessage.includes("ti yare")) {
    return responses.headache
  }

  if (lowerMessage.includes("fever") || lowerMessage.includes("ɔhyew") || lowerMessage.includes("temperature")) {
    return responses.fever
  }

  if (lowerMessage.includes("cough") || lowerMessage.includes("wa")) {
    return responses.cough
  }

  return responses.default
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json()
    const { message, language, history } = body

    // Simulate API processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Generate response based on message content and language
    const response = getHealthResponse(message, language)

    return NextResponse.json({
      response,
      language,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}
