module Main where

import Prelude

import Control.Monad.Aff (launchAff_)
import Control.Monad.Eff (Eff)
import Control.Monad.Eff.Class (liftEff)
import Control.Monad.Eff.Console (CONSOLE, log, logShow)
import Data.Argonaut.Core (Json)
import Data.Argonaut.Parser (jsonParser)
import Data.Codec (decode)
import Data.Codec.Argonaut (printJsonDecodeError)
import Data.Either (Either(..))
import HashFramework.Codec as HF.Codec
import Network.HTTP.Affjax (AJAX, get)

main :: forall e. Eff ( console :: CONSOLE, ajax :: AJAX | e ) Unit
main = launchAff_ do
  res <- get "task/1/"
  liftEff $ log res.response
  let jsonP = jsonParser res.response :: Either String Json
  liftEff case jsonP of
    Left err -> log err
    Right json -> case decode HF.Codec.task json of
      Left err ->
        log $ printJsonDecodeError err
      Right task ->
        logShow task.started
  pure unit
