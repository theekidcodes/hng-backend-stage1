import httpx
from typing import Optional, Dict, Any
import asyncio


class ExternalAPIService:
    """Service to call external APIs for demographic data"""
    
    BASE_URLS = {
        "genderize": "https://api.genderize.io",
        "agify": "https://api.agify.io",
        "nationalize": "https://api.nationalize.io"
    }
    
    @staticmethod
    async def get_gender(name: str) -> Dict[str, Any]:
        """
        Call Genderize API to get gender prediction
        
        Returns:
            {
                "gender": "male" | "female" | None,
                "probability": float,
                "count": int
            }
        
        Raises:
            Exception if API returns invalid data
        """
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    ExternalAPIService.BASE_URLS["genderize"],
                    params={"name": name}
                )
                response.raise_for_status()
                data = response.json()
                
                # Validate response
                if data.get("gender") is None or data.get("count") == 0:
                    raise ValueError("Genderize returned null gender or count=0")
                
                return {
                    "gender": data["gender"],
                    "probability": data.get("probability", 0),
                    "count": data.get("count", 0)
                }
            except Exception as e:
                raise Exception(f"Genderize API error: {str(e)}")
    
    @staticmethod
    async def get_age(name: str) -> Dict[str, Any]:
        """
        Call Agify API to get age prediction
        
        Returns:
            {
                "age": int,
                "count": int
            }
        
        Raises:
            Exception if API returns invalid data
        """
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    ExternalAPIService.BASE_URLS["agify"],
                    params={"name": name}
                )
                response.raise_for_status()
                data = response.json()
                
                # Validate response
                if data.get("age") is None:
                    raise ValueError("Agify returned null age")
                
                return {
                    "age": data["age"],
                    "count": data.get("count", 0)
                }
            except Exception as e:
                raise Exception(f"Agify API error: {str(e)}")
    
    @staticmethod
    async def get_nationality(name: str) -> Dict[str, Any]:
        """
        Call Nationalize API to get nationality prediction
        
        Returns:
            {
                "country_id": "NG" | "US" | etc,
                "probability": float
            }
        
        Raises:
            Exception if API returns no country data
        """
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    ExternalAPIService.BASE_URLS["nationalize"],
                    params={"name": name}
                )
                response.raise_for_status()
                data = response.json()
                
                # Get countries list
                countries = data.get("country", [])
                
                if not countries:
                    raise ValueError("Nationalize returned no country data")
                
                # Pick country with highest probability
                top_country = max(countries, key=lambda x: x.get("probability", 0))
                
                return {
                    "country_id": top_country.get("country_id"),
                    "probability": top_country.get("probability", 0)
                }
            except Exception as e:
                raise Exception(f"Nationalize API error: {str(e)}")
    
    @staticmethod
    def classify_age_group(age: int) -> str:
        """
        Classify age into groups
        0-12: child
        13-19: teenager
        20-59: adult
        60+: senior
        """
        if age < 0:
            return "unknown"
        elif age <= 12:
            return "child"
        elif age <= 19:
            return "teenager"
        elif age <= 59:
            return "adult"
        else:
            return "senior"
    
    @staticmethod
    async def get_all_data(name: str) -> Optional[Dict[str, Any]]:
        """
        Call all three APIs concurrently and combine results
        
        Returns:
            {
                "gender": str,
                "gender_probability": float,
                "sample_size": int,
                "age": int,
                "age_group": str,
                "country_id": str,
                "country_probability": float
            }
        
        Returns None if any API fails or returns invalid data
        """
        try:
            # Call all three APIs concurrently
            gender_task = ExternalAPIService.get_gender(name)
            age_task = ExternalAPIService.get_age(name)
            nationality_task = ExternalAPIService.get_nationality(name)
            
            gender_data, age_data, nationality_data = await asyncio.gather(
                gender_task,
                age_task,
                nationality_task,
                return_exceptions=True
            )
            
            # Check for exceptions
            if isinstance(gender_data, Exception):
                raise Exception(f"Genderize returned an invalid response")
            if isinstance(age_data, Exception):
                raise Exception(f"Agify returned an invalid response")
            if isinstance(nationality_data, Exception):
                raise Exception(f"Nationalize returned an invalid response")
            
            # Combine all data
            age_group = ExternalAPIService.classify_age_group(age_data["age"])
            
            return {
                "gender": gender_data["gender"],
                "gender_probability": gender_data["probability"],
                "sample_size": gender_data["count"],
                "age": age_data["age"],
                "age_group": age_group,
                "country_id": nationality_data["country_id"],
                "country_probability": nationality_data["probability"]
            }
        
        except Exception as e:
            # Return None to signal API failure
            print(f"Error fetching external data: {str(e)}")
            return None
