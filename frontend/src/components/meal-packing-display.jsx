"use client"

import React, { useState } from "react"
import { Card } from "./ui/card"
import { Button } from "./ui/button"
import { MapPin, AlertCircle } from "lucide-react"
import { fetchScanResult } from "../lib/api"
import "./meal-packing-display.css"

export default function MealPackingDisplay() {
  const [orderNumber, setOrderNumber] = useState("")
  const [currentMeal, setCurrentMeal] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!orderNumber.trim()) return

    setIsLoading(true)
    setError(null)
    try {
      const result = await fetchScanResult(orderNumber.trim())
      setCurrentMeal(result)
    } catch (err) {
      setError("Failed to fetch meal data. Please try again.")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="meal-packing-container">

      {/* 🔍 Input bar: Always visible */}
      <div className="input-section">
        <input
          type="text"
          placeholder="Enter Order Number"
          value={orderNumber}
          onChange={(e) => setOrderNumber(e.target.value)}
          className="order-input"
        />
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? "Loading..." : "Submit"}
        </Button>
      </div>

      {/* 🧾 Main card with content */}
      <Card className="meal-display-card">
        {isLoading ? (
          <div className="loading-screen">
            <h1 className="loading-title">Loading...</h1>
            <p className="loading-text">Retrieving meal information</p>
          </div>
        ) : error ? (
          <div className="error-screen">
            <AlertCircle className="error-icon" />
            <h1 className="error-title">Error</h1>
            <p className="error-text">{error}</p>
            <Button className="try-again-button" onClick={() => setError(null)}>
              Try Again
            </Button>
          </div>
        ) : currentMeal ? (
          <div className="meal-info-container">
            <div className="meal-header">
              <div className="meal-details">
                <div className="meal-details-list">
                  <div className="meal-detail-item">{currentMeal.clientName}</div>
                  <div className="meal-detail-item">{currentMeal.dishName}</div>
                  <div className="meal-detail-item">
                    {currentMeal.mealType} – {currentMeal.dishNumber} – Station:{" "}
                    {currentMeal.stationNumber}
                  </div>
                </div>
              </div>
              {currentMeal.dietaryRestrictions && (
                <div className="dietary-restrictions">
                  <div className="dietary-title">DIETARY RESTRICTIONS:</div>
                  <div className="dietary-text">
                    {currentMeal.dietaryRestrictions}
                  </div>
                </div>
              )}
            </div>

            <div className="ingredients-container">
              <div className="ingredients-list">
                {currentMeal.ingredients.map((ingredient, idx) => (
                  <div key={idx} className="ingredient-card">
                    <h2 className="ingredient-name">{ingredient.name}</h2>
                    <p className="ingredient-portion">{ingredient.portion}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="ready-screen">
            <div className="station-display">
              <MapPin className="station-icon" />
              <h2 className="station-text">—</h2>
            </div>
            <h1 className="ready-title">Enter Order Number</h1>
            <p className="ready-text">
              Submit a barcode or order ID to display meal information
            </p>
          </div>
        )}
      </Card>
    </div>
  )
}