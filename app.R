#!/usr/bin/env Rscript

#NOTES:
#1. 

library(shiny)
library(DT)
library(gridExtra)
library(grid)
library(shinythemes)
library(shinycssloaders)
library(shinyjs)
library(data.table)

# increase max upload table size
options(shiny.maxRequestSize = 100*1024^2)

#read in stages strings  to make drop down menu
stage_lst <- read.table("files/stagelabel.txt", sep="\n") #save stages from filefrom file  to variable
stages <- as.character(stage_lst$V1)
stages <- c(stages,"All Stages") #add 'All Stages' option
stages <- stages[c(length(stages),1:(length(stages)-1))] #move 'All_Stages' to top of list
stages <- gsub(":", " ", stages)

# Define UI ----
ui <- fluidPage(

  #HEADER & GENERAL UI
  theme = shinytheme("flatly"),
  a(href='https://zfin.org/',img(src='zfin_img.jpg',height='65',align = "left", style = "margin-top:25px;margin-left:60px;")),
  titlePanel(h1(img(src='zfin_fish.png', height='65', style = "padding-bottom:20px;"), "DEATS: A Zebrafish Cell Type Identification Tool",
             align = "center",
             style = "color:#000000;padding-bottom:5px;margin-left:400px;margin-right:75px;font-family: Book Antigua;"
           ),
            windowTitle = "DEATS: A Zebrafish Cell-Type Identification Tool"
        ),
  sidebarLayout(
    sidebarPanel(width = 4,

      #DEATS GENERAL INFO
      helpText("Welcome to the DEATS Web App"),
      helpText("Please see our", a("github repo", href="https://github.com/pranavs22/DEATS"), "to learn more about the DEATS project"),
      hr(style = "border-color: #18BC9C;"),

      #DEV STAGE UI
      helpText("1. Choose Developmental Stage", style ="color:#2C3F51;font-weight: bold;padding-bottom:13px;"),
      selectInput("stage",
                  label = NULL,
                  choices = c("",stages),
                  selected = "All Stages"),
      hr(style = "border-color: #18BC9C;"),

      #SINGLE DEG SET UI
      helpText("2. Upload Single DEG Set or Multiple DEG Sets", style ="color:#2C3F51;font-weight: bold;"),
      helpText("A. Paste in Single DEG Set", style = "color:#2C3F51;font-weight: bold;padding-top:13px;"),
      actionLink("example_sdeg_link", label="Click here for an example Single DEG Set", style = "color: #2C3F51;font-weight: bold;font-size: small;text-align: center;padding-left:10px;"),
      verbatimTextOutput("example_sdeg_set"),
      textAreaInput("sdeg_set",
                label = NULL,
                height = "100px",
                placeholder = "e.g. ENSDARG00001\n\tENSDARG00002\n\tENSDARG00003 \n\tENSDARG00004 ..."),

      #MULTI DEG SET UI
      helpText("B. Upload Multiple DEG Sets", style = "color:#2C3F51;font-weight:bold;padding-top:20px;"),
      actionLink("example_mdeg_link", label="Click here to upload an example Multiple DEG Set", style = "color: #2C3F51;font-weight: bold;font-size: small;text-align: center;padding-left:10px;"),
      textOutput("ex_mdeg_loaded"),
      fileInput("mdeg_set",
                 label = NULL,
                 accept = c(".tsv"),
                 buttonLabel = "Upload"),
       # helpText("Choose PETE Score Filter", helpText("(details", a("here)", href="https://github.com/pranavs22/DEATS", style="font-size: 13px;"), style="font-weight:normal;font-size: 13px"), style ="color: #2C3F51;font-weight: bold;font-size: small;padding-left:10px;"),
       textInput("pete",
                 label = NULL,
                 width = "60px",
                 placeholder = "0",
                 value = 0),
      tags$style(type = 'text/css', '#pete {text-align: center;}'),
      helpText("Information on PETE score and format required for Multiple DEG Set uploads can be found", a("here", href="https://github.com/pranavs22/DEATS", style= "font-size: 14px;"), style= "font-size: 14px;text-align:center;padding-top:3px;padding-bottom:-5;"),
      hr(style = "border-color: #18BC9C;"),

      #GO!
      actionButton("action", label = "Go"),
      textOutput("upload_deg"),
      textOutput("execute_python"),
      tags$style(type = 'text/css', '#ex_mdeg_loaded {color: #2C3F51;font-weight: bold;font-size: small;text-align: right;}'),
      inlineCSS(list(".shiny-input-container" = "margin-bottom: 0px",
               "#mdeg_set_progress" = "margin-bottom: 0px",
               ".checkbox" = "margin-top: 0px"))
    ),

    #TAB PANELS UI
    mainPanel(
       tabsetPanel(
         type = "tabs",

         #DEG UI
         tabPanel("Differentially Expressed Genes (DEG)", tableOutput("sdeg_tbl")),

         #DEATS UI
         tabPanel("Differentially Expressed Anatomy Terms (DEATS)",
            style = "margin-top:10px;",

            #FILE HANDLING
            column(3,
              selectInput("csv_num", "Cluster Number", choices=NULL, selected = NULL),
              hr(style = "border-color: #18BC9C;"),
              textInput("file_rename", label = "Annotate Cell Type"),
              actionButton('submit','Submit'),
              helpText("Read more about cell type annotations", a("here", href="https://github.com/2019-bgmp/bgmp-group-project-scrnaseq_zebrafish/blob/master/Shiny/seve_master/zfin_app/README.md")),
              hr(style = "border-color: #18BC9C;"),
              downloadButton("downloadData", "Download DEATS")),

            #DEATS TABLE UI
            column(7,
              # tableOutput("mdeg_tbl"),
              dataTableOutput("mdeg_tbl"),
              textOutput("rename_metadata")),

            #GENE SYMBOLS UI
            column(1,
              useShinyjs(),
              actionButton('see_sym', 'See Gene Symbols',style='padding:10px;font-size:95%;'),
              tableOutput("gene_sym"))

            )
          )
        )
      )
)

# Define server logic ----
server <- function(input, output, session) {


  #SET LOGIC OPERATORS AND HANDLE EXAMPLE SETS
  observeEvent(input$sdeg_set, {
    system("touch files/single_deg_on")
    system("echo processing single DEG set")
    if (file.exists("files/multi_deg_on")){
          file.remove("files/multi_deg_on")
        }
  }, ignoreInit = TRUE)
  observeEvent(input$mdeg_set, {
    system("touch files/multi_deg_on")
    system("echo processing multi DEG set")
    if (file.exists("files/single_deg_on")){
          file.remove("files/single_deg_on")
        }
  })
  observeEvent(input$example_sdeg_link, {
    toggle("example_sdeg_set")
    output$example_sdeg_set <- renderText({"Germ cell Primordial\n\nENSDARG00000075217\nENSDARG00000022813\nENSDARG00000040510\nENSDARG00000059951\nENSDARG00000089181\nENSDARG00000008454\nENSDARG00000068255\nENSDARG00000089802\nENSDARG00000069758\nENSDARG00000099586\nENSDARG00000044549\nENSDARG00000109565"
    })
  })
  observeEvent(input$example_mdeg_link, {
    system("touch files/example_multi_set")
    system("touch files/multi_deg_on")
    system("echo processing example multi deg set")
    if (file.exists("files/single_deg_on")){
          file.remove("files/single_deg_on")
        }
    output$ex_mdeg_loaded <- renderText({
      Sys.sleep(0.45)
      "File Uploaded"
    })
  })

  #ACTION BUTTON FUNCTION
  observeEvent(input$action, {

    #SINGLE DEG HANDLING
    if (file.exists("files/single_deg_on")){

      #SHOW SINGLE DEG TABLE
      output$sdeg_tbl <- renderTable({
        unlist(strsplit(input$sdeg_set, "\n"))
      })

      #SAVE SINGLE DEG TO A FILE
      output$upload_deg <- renderText({
        if (file.exists("files/sdeg_set.tsv")){
          file.remove("files/sdeg_set.tsv")
        }
        var <- paste0(input$sdeg_set,"\n")
        cat(var, file="files/sdeg_set.tsv")
      })

      #EXECUTE SCRIPT
      output$execute_python <- renderText({
        withProgress(message = 'Making Tables', value = 1, {
          stage_cmd <- input$stage
          if(stage_cmd == "All Stages"){
            stage_cmd = "all_stages"
          }
          if(grepl(" ", stage_cmd, fixed=TRUE)){
            stage_cmd <- gsub(" ","_",stage_cmd)
          }
          cmd <- c("./main.py",
                 "-zfin_data", "files/zfin_wt_expression.json",
                 "-single_set", "files/sdeg_set.tsv",
                 "-zfa", "files/zfa_ids.txt",
                 "-bspo", "files/bspo_cleaned.txt",
                 "-stage_file", "files/stagelabel.txt",
                 "-pete_score", "0",
                 "-stage_str", "all_stages")
          cmd[[15]] <- as.character(req(stage_cmd))
          cmd <- paste(unlist(cmd), collapse=' ')
          system(cmd)
          system("rm -r sym_data || true")
          system("cp -r meta_data sym_data")
        })
      })

      #SHOW SCRIPT DATA OUTPUT
      observe({
        f_lst <- list.files("data/")
        f_lst <- sub(".csv", "", f_lst, fixed = TRUE)
        updateSelectInput(session, "csv_num", choices = sort(as.numeric(f_lst)))
        output$mdeg_tbl <- renderDataTable({ ####renderDataTable
          data_tbl <- read.csv("data/data.csv", check.names=FALSE, header = FALSE, col.names = c("anatomy.term", "Count"))
          dist_tbl <- read.csv("stats/dist.csv", col.names = c("anatomy.term", "Count"), header=F)
          combined_tbl <- merge(dist_tbl,data_tbl, by = "anatomy.term")
          combined_tbl$not_count.x <- sum(combined_tbl$Count.x) - combined_tbl$Count.x
          combined_tbl$not_count.y <- sum(combined_tbl$Count.y) - combined_tbl$Count.y
          combined_tbl <- combined_tbl[c(1,2,4,3,5)]
          combined_tbl$p.val <- apply(combined_tbl, 1,
                        function(x) {
                          tbl <- matrix(as.numeric(x[2:5]), ncol=2, byrow=T)
                          fisher.test(tbl, alternative="two.sided")$p.value
                        })
          combined_tbl <- combined_tbl[,c(1,4,6)]
          colnames(combined_tbl) <- c("Anatomy Term", "Count","p val")
          combined_tbl <- combined_tbl[order((combined_tbl$"Count"),decreasing = TRUE),]


          combined_tbl$"p val" <- round(combined_tbl$"p val",5)###
          # combined_tbl$"p val" <- format(round(combined_tbl$"p val",5), scientific=T)###
          #format(round(0.000538063809520502,5), scientific=T)

          # combined_tbl
          validate(
                  need(nrow(combined_tbl) > 0, "With these filters there is no data to show")
                         )
          # combined_tbl
          datatable(combined_tbl,rownames = FALSE)
        })
      })

      #SHOW GENE SYMBOLS TOGGLE
      observeEvent(input$see_sym,{
        gene_sym_tbl <- read.table("sym_data/meta_data.csv", check.names=FALSE, header = FALSE, sep = "\t")
        toggle("gene_sym")
        output$gene_sym <- renderTable({
          gene_sym_tbl$V2
        })
      })

      #RENAME METADATA OUTPUT
      observeEvent(input$submit,{
        output$rename_metadata <- renderText({
          # file.rename("meta_data/meta_data.csv", paste0("meta_data/", input$file_rename, ",", input$stage, ",", Sys.Date(), ".csv"))
          file.rename("meta_data/meta_data.csv", paste0("meta_data/", gsub(" ", "_", input$file_rename), ",", gsub(" ", "_", input$stage), ",", Sys.Date(), ".csv"))
        })
      })

      #DOWNLOAD DATA HANDLING
      output$downloadData <- downloadHandler(
        filename = function() {
          paste0(input$stage, ",", Sys.Date(), ".csv")
          },
        content = function(file) {
          write.table(read.csv("data/data.csv", header = FALSE, col.names = c("Anatomy Term", "Count")), file)
          }
      )
    }

    #MULTI_DEG HANDLING
    if (file.exists("files/multi_deg_on")){

      #SHOW MULTI_DEG TABLE
      output$sdeg_tbl <- renderTable({

        req(input$mdeg_set)
        mdeg_set <- read.table(input$mdeg_set$datapath)
        colnames(mdeg_set) <-c("pVal", "Average_LogFC", "pct1", "pct2", "pVal (adj)", "Cluster Number", "Gene Name")
        mdeg_set$PETEScore <- (mdeg_set$pct1 / mdeg_set$pct2) * (mdeg_set$Average_LogFC)
        mdeg_set$"Cluster Number" <- as.integer(mdeg_set$"Cluster Number" + 1)
        mdeg_set <- mdeg_set[c(6,7,8)]
        if (input$pete != 0){
          mdeg_set <- setorder(setkey(setDT(mdeg_set), "Cluster Number"), "Cluster Number", -"PETEScore")[
            ,.SD[1:input$pete], by="Cluster Number"]
        }
        if (input$pete == 0){
          mdeg_set <- setorder(setkey(setDT(mdeg_set), "Cluster Number"), "Cluster Number", -"PETEScore")[
            ,.SD[1:length(mdeg_set$PETEScore)], by="Cluster Number"]
        }
        na.omit(mdeg_set)
      })

      #USE EXAMPLE FILE
      if (file.exists("files/example_multi_set")){
        output$sdeg_tbl <- renderTable({
          mdeg_set <- read.table("files/example_multi_deg_set.tsv")
          colnames(mdeg_set) <-c("pVal", "Average_LogFC", "pct1", "pct2", "pVal (adj)", "Cluster Number", "Gene Name")
          mdeg_set$PETEScore <- (mdeg_set$pct1 / mdeg_set$pct2) * (mdeg_set$Average_LogFC)
          mdeg_set$"Cluster Number" <- as.integer(mdeg_set$"Cluster Number" + 1)
          mdeg_set <- mdeg_set[c(6,7,8)]
          if (input$pete != 0){
            mdeg_set <- setorder(setkey(setDT(mdeg_set), "Cluster Number"), "Cluster Number", -"PETEScore")[
              ,.SD[1:input$pete], by="Cluster Number"]
          }
          if (input$pete == 0){
            mdeg_set <- setorder(setkey(setDT(mdeg_set), "Cluster Number"), "Cluster Number", -"PETEScore")[
              ,.SD[1:length(mdeg_set$PETEScore)], by="Cluster Number"]
          }
          na.omit(mdeg_set)
        })
      }

      #SAVE MULTI_DEG TO A FILE
      output$upload_deg <- renderText({
        if (file.exists("files/mdeg_set.tsv")){
          file.remove("files/mdeg_set.tsv")
        }
        inFile <- input$mdeg_set
        file.copy(inFile$datapath, file.path("files", "mdeg_set.tsv"))
      })

      #EXECUTE SCRIPT
      output$execute_python <- renderText({
        withProgress(message = 'Making Tables', value = 1, {
          stage_cmd <- input$stage
          pete_cmd <- input$pete
          if(stage_cmd == "All Stages"){
            stage_cmd = "all_stages"
          }
          if(grepl(" ", stage_cmd, fixed=TRUE)){
            stage_cmd <- gsub(" ","_",stage_cmd)
          }
          cmd <- c("./main.py",
                 "-zfin_data", "files/zfin_wt_expression.json",
                 "-multiple_set", "files/mdeg_set.tsv",
                 "-zfa", "files/zfa_ids.txt",
                 "-bspo", "files/bspo_cleaned.txt",
                 "-stage_file", "files/stagelabel.txt",
                 "-pete_score", "0",
                 "-stage_str", "NA")
           if (file.exists("files/example_multi_set")){
             cmd[[5]] <- "files/example_multi_deg_set.tsv"
             file.remove("files/example_multi_set")
             system("echo using example multi deg set")
           }
          cmd[[15]] <- as.character(req(stage_cmd))
          cmd[[13]] <- as.character(pete_cmd)
          cmd <- paste(unlist(cmd), collapse=' ')
          system(cmd)
          system("rm -r sym_data || true")
          system("cp -r meta_data sym_data")
        })
      })

      #SHOW SCRIPT DATA OUTPUT
      observe({
        f_lst <- list.files("data/")
        f_lst <- sub(".csv", "", f_lst, fixed = TRUE)
        updateSelectInput(session, "csv_num", choices = sort(as.numeric(f_lst)))
        output$mdeg_tbl <- renderDataTable({
          data_tbl <- read.csv(paste0("data/",input$csv_num,".csv"), check.names=FALSE, header = FALSE, col.names = c("anatomy.term", "Count"))
          dist_tbl <- read.csv("stats/dist.csv", col.names = c("anatomy.term", "Count"), header=F)
          combined_tbl <- merge(dist_tbl,data_tbl, by = "anatomy.term")
          combined_tbl$not_count.x <- sum(combined_tbl$Count.x) - combined_tbl$Count.x
          combined_tbl$not_count.y <- sum(combined_tbl$Count.y) - combined_tbl$Count.y
          combined_tbl <- combined_tbl[c(1,2,4,3,5)]
          combined_tbl$p.val <- apply(combined_tbl, 1,
                        function(x) {
                          tbl <- matrix(as.numeric(x[2:5]), ncol=2, byrow=T)
                          fisher.test(tbl, alternative="two.sided")$p.value
                        })
          combined_tbl <- combined_tbl[,c(1,4,6)]
          colnames(combined_tbl) <- c("Anatomy Term", "Count","p val")
          combined_tbl <- combined_tbl[order((combined_tbl$"Count"),decreasing = TRUE),]

          combined_tbl$"p val" <- round(combined_tbl$"p val",5)###
          # combined_tbl$"p val" <- format(round(combined_tbl$"p val",5), scientific=T)###
          # format(round(0.000538063809520502,5), scientific=T)

          # combined_tbl
          validate(
                  need(nrow(combined_tbl) > 0, "With these filters there is no data to show")
                         )
          # combined_tbl
          datatable(combined_tbl,rownames = FALSE)
        })
      })

      #SHOW GENE SYMBOLS TOGGLE
      observeEvent(input$see_sym,{
        gene_sym_tbl <- read.table(paste0("sym_data/",input$csv_num,".csv"), check.names=FALSE, header = FALSE, sep = "\t")
        toggle("gene_sym")
        output$gene_sym <- renderTable({
          gene_sym_tbl$V2
        })
      })

      #RENAME METADATA OUTPUT
      observeEvent(input$submit,{
        observeEvent(input$file_rename,{
            file.rename(paste0("meta_data/",input$csv_num,".csv"), paste0("meta_data/", gsub(" ", "_", input$file_rename), ",", gsub(" ", "_", input$stage), ",", Sys.Date(), ".csv"))
          })
      })

      #DOWNLOAD DATA HANDLING
      output$downloadData <- downloadHandler(
        filename = function() {
          paste0(input$stage, ",", Sys.Date(), ".csv")
          },
        content = function(file) {
          write.table(read.csv(paste0("data/",input$csv_num,".csv"), header = FALSE, col.names = c("Anatomy Term", "Count")), file)
          }
      )
    }
})
}

# Run the app ----
shinyApp(ui = ui, server = server)
