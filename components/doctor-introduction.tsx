"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Stethoscope, Heart, Award, MapPin, Clock, Star } from "lucide-react"

interface DoctorIntroductionProps {
  avatar: "male" | "female"
  onStartConsultation: () => void
}

const doctorInfo = {
  female: {
    name: "Dr. Ama Osei",
    title: "General Practitioner & Family Medicine Specialist",
    experience: "8 years",
    location: "Accra, Ghana",
    specialties: ["Family Medicine", "Preventive Care", "Women's Health", "Pediatrics"],
    languages: ["English", "Akan", "Twi", "Ga"],
    rating: 4.9,
    consultations: "2,500+",
    greeting:
      "Akwaaba! I'm Dr. Ama Osei, and I'm delighted to meet you today. As your AI doctor, I can see, hear, and interact with you just like an in-person consultation. I specialize in family medicine and I'm here to provide you with personalized healthcare guidance in both English and Akan.",
    credentials: [
      "MD - University of Ghana Medical School",
      "Board Certified Family Medicine",
      "Fellowship in Preventive Medicine",
      "Licensed Medical Practitioner - Ghana Medical & Dental Council",
    ],
    image: "/placeholder.svg?height=300&width=250",
  },
  male: {
    name: "Dr. Kwame Asante",
    title: "Internal Medicine Specialist & Adult Healthcare Expert",
    experience: "10 years",
    location: "Kumasi, Ghana",
    specialties: ["Internal Medicine", "Chronic Disease Management", "Diabetes Care", "Hypertension"],
    languages: ["English", "Akan", "Twi"],
    rating: 4.8,
    consultations: "3,200+",
    greeting:
      "Good day! I'm Dr. Kwame Asante, your AI internal medicine specialist. I'm equipped with advanced AI capabilities that allow me to see, hear, and communicate with you naturally. With over 10 years of experience in adult healthcare, I'm here to provide you with comprehensive medical guidance in both English and Akan.",
    credentials: [
      "MD - Kwame Nkrumah University of Science & Technology",
      "Internal Medicine Residency - Komfo Anokye Teaching Hospital",
      "Board Certified Internal Medicine",
      "Specialist in Chronic Disease Management",
    ],
    image: "/placeholder.svg?height=300&width=250",
  },
}

export function DoctorIntroduction({ avatar, onStartConsultation }: DoctorIntroductionProps) {
  const doctor = doctorInfo[avatar]

  return (
    <Card className="mb-6 bg-gradient-to-br from-blue-50 via-white to-green-50 border-2 border-blue-100 shadow-lg">
      <CardContent className="p-6">
        <div className="flex flex-col lg:flex-row items-start gap-6">
          {/* Doctor Image */}
          <div className="relative">
            <div className="w-64 h-80 rounded-xl overflow-hidden border-4 border-white shadow-xl bg-white">
              <img
                src={doctor.image || "/placeholder.svg"}
                alt={doctor.name}
                className="w-full h-full object-cover object-top"
              />
            </div>
            <div className="absolute -bottom-2 -right-2 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
              AI POWERED
            </div>
          </div>

          {/* Doctor Information */}
          <div className="flex-1 space-y-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-gray-800">{doctor.name}</h2>
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                  <span className="text-sm font-semibold text-gray-700">{doctor.rating}</span>
                </div>
              </div>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800 mb-3">
                <Stethoscope className="h-3 w-3 mr-1" />
                {doctor.title}
              </Badge>
              <p className="text-gray-700 leading-relaxed">{doctor.greeting}</p>
            </div>

            {/* Stats Row */}
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-1 text-gray-600">
                <Award className="h-4 w-4 text-blue-600" />
                <span className="font-medium">{doctor.experience} Experience</span>
              </div>
              <div className="flex items-center gap-1 text-gray-600">
                <MapPin className="h-4 w-4 text-green-600" />
                <span>{doctor.location}</span>
              </div>
              <div className="flex items-center gap-1 text-gray-600">
                <Clock className="h-4 w-4 text-purple-600" />
                <span>{doctor.consultations} Consultations</span>
              </div>
            </div>

            {/* Specialties */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <Heart className="h-4 w-4 text-red-500" />
                Medical Specialties
              </h4>
              <div className="flex flex-wrap gap-2">
                {doctor.specialties.map((specialty, index) => (
                  <Badge key={index} variant="outline" className="bg-white border-blue-200 text-blue-700">
                    {specialty}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Languages */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Languages Spoken</h4>
              <p className="text-gray-600">{doctor.languages.join(" • ")}</p>
            </div>

            {/* Credentials */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Medical Credentials</h4>
              <div className="space-y-1">
                {doctor.credentials.map((credential, index) => (
                  <p key={index} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    {credential}
                  </p>
                ))}
              </div>
            </div>

            {/* Start Consultation Button */}
            <div className="pt-4">
              <Button
                onClick={onStartConsultation}
                className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white px-8 py-3 text-lg font-semibold shadow-lg"
              >
                Begin AI Consultation with {doctor.name.split(" ")[1]}
              </Button>
              <p className="text-xs text-gray-500 mt-2">
                🤖 This AI doctor can see, hear, and speak with you naturally
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
