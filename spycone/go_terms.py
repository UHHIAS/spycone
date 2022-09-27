
# """
# Created on Fri Sep  6 10:37:15 2019

# @author: alexander
# """
from collections import defaultdict
from logging import raiseExceptions

import pandas as pd
import numpy as np
import os, sys
from gprofiler import GProfiler 
import time
import warnings


sys.path.insert(0, os.path.abspath('./_NEASE/nease/'))
from ._NEASE.nease import nease
from ._util_stat.multipletesting import pvalue_correction

# Disable
def _blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def _enablePrint():
    sys.stdout = sys.__stdout__




def list_gsea(genelist, species, gene_sets=None, is_results=None, p_adjust_method="fdr_bh", cutoff=0.05, method="gsea", term_source="all"):
    """
    Perform gene set enrichment on a list of gene
    """
    geneset_map = {10090:['KEGG_2019_Mouse'], 9606:['KEGG_2019_Human']}
    org_map = {10090:'Mouse', 9606:'Human'}
    bg = {10090:'mmusculus_gene_ensembl', 9606:'hsapiens_gene_ensembl'}

    if method == "gsea":
    
        gpro = GProfiler(return_dataframe=True)
        enrh = gpro.profile(organism=species,
                query=genelist, no_evidences=False)
        
        mct = pvalue_correction(enrh['p_value'], method=p_adjust_method)
        enrh['adj_pval'] = mct.corrected_pvals
        enrh =enrh[enrh['adj_pval']<cutoff]

        enr = pd.concat([enrh])
        enr = enr.reset_index(drop=True)
        if term_source != "all":
            enr_results[u].append(enr[enr['source']=="all"])
        
        enr_results = enr.results[enr.results['Adjusted P-value']<cutoff]
        time.sleep(2)

        print("---------Gene Set Enrichment Result---------\n", file=sys.__stdout__)
        print(f"Method: {method} Database: {gene_sets}", file=sys.__stdout__)
        print(f"{len(genelist)} of genes found enriched in {enr_results.shape[0]} terms.", file=sys.__stdout__)
        print("-----END-----", file=sys.__stdout__)
        
        return enr_results


def clusters_gsea(DataSet, species, gene_sets=None, is_results=None, cutoff=0.05, p_adjust_method="fdr_bh", method="nease", term_source="all"):
    """
    Perform gene set enrichment on clusters (cluster object)

    """
    
    geneset_map = {10090:['KEGG_2019_Mouse'], 9606:['KEGG_2019_Human']}
    org_map = {10090:'Mouse', 9606:'Human'}
    bg = {10090:'mmusculus_gene_ensembl', 9606:'hsapiens_gene_ensembl'}
    X = DataSet.clusterobj
    
    _blockPrint()
    warnings.simplefilter("ignore")
    if method == "gsea":

        enr_results = defaultdict(list)
        for u,v in X.symbs_clusters.items():
            gpro = GProfiler(return_dataframe=True)
            enrh = gpro.profile(organism=species,
                    query=X.symbs_clusters[u], no_evidences=False)
            
            mct = pvalue_correction(enrh['p_value'], method=p_adjust_method)
            enrh['adj_pval'] = mct.corrected_pvals
            enrh =enrh[enrh['adj_pval']<cutoff]
            enrh['cluster'] = f"Cluster {u}"

            enr = pd.concat([enrh])
            enr = enr.reset_index(drop=True)
            
            if term_source != "all":
                enr_results[u].append(enr[enr['source']==term_source])
            else:
                enr_results[u].append(enr)
            time.sleep(2)

        print("---------Gene Set Enrichment Result---------\n", file=sys.__stdout__)
        print(f"Method: {method} ", file=sys.__stdout__)
        for u,v in enr_results.items():
            print("Cluster {}".format(u)," found enriched in {} terms.".format(v[0].shape[0]), file=sys.__stdout__)
        print("-----END-----", file=sys.__stdout__)
        
        return enr_results, None

    if method == "nease":
        nease_support = ['PharmGKB','HumanCyc','Wikipathways','Reactome','KEGG','SMPDB','Signalink','NetPath','EHMN','INOH','BioCarta','PID']

        ##default database == "KEGG"
        if gene_sets is None:
            gene_sets = ["KEGG"]

        check_support_database = [True if geneset not in nease_support else False for geneset in gene_sets]
        if np.sum(check_support_database) > 0:
            raise ValueError("Please input a supported database: ['PharmGKB','HumanCyc','Wikipathways','Reactome','KEGG','SMPDB','Signalink','NetPath','EHMN','INOH','BioCarta','PID']")

        if is_results is None:
            raise ValueError("Please provide the result dataframe of isoform switch detection for nease enrichment.")

        _blockPrint()
        enr_results = defaultdict(list)
        nease_obj = defaultdict(list)
        for u,v in X.genelist_clusters.items():
            subset = is_results[is_results['gene'].astype(str).isin(list(map(lambda x: str(int(x)), v)))]
            nease_input = []
            for eachrow in subset.iterrows():
                domains = eachrow[1]['exclusive_domains']
                if len(domains)>0:
                    for domain in domains:
                        nease_input.append(str(eachrow[1]['gene'])+"/"+domain)

            if len(nease_input)>0:
                nease_input = pd.DataFrame({"domain":nease_input})
                events=nease.run(nease_input, organism="Human", input_type="Spycone")
                nease_enr=events.enrich(database=gene_sets)

                if nease_enr is not None:
                    nease_enr=nease_enr.rename(columns = {'adj p_value':'Adjusted P-value'})
                    nease_enr=nease_enr.rename(columns = {'Pathway name':'Term'})
                    nease_obj[u].append(events)
                    enr_results[u].append(nease_enr[nease_enr['Adjusted P-value']<cutoff])
                else:
                    continue
            else:
                continue
        
        print("---------Gene Set Enrichment Result---------\n", file=sys.__stdout__)
        print(f"Method: {method} Database: {gene_sets}", file=sys.__stdout__)
        for u,v in enr_results.items():
            print("Cluster {}".format(u)," found enriched in {} terms.".format(v[0].shape[0]), file=sys.__stdout__)
        print("-----END-----", file=sys.__stdout__)
        
        return enr_results, nease_obj

def modules_gsea(X, clu, species, type="PPI", p_adjust_method="fdr_bh", cutoff=0.05, method="nease", term_source="all"):
    """
    Perform gene set enrichment on network modules after domino
    """
    geneset_map = {10090:['KEGG_2019_Mouse'], 9606:['KEGG_2019_Human']}
    mapping = dict(zip(clu.DataSet.gene_id, clu.DataSet.symbs))
    org_map = {10090:'Mouse', 9606:'Human'}
    bg = {10090:'mmusculus_gene_ensembl', 9606:'hsapiens_gene_ensembl'}
    enr_results = defaultdict(lambda: defaultdict(list))

    warnings.simplefilter("ignore")


    if isinstance(X, list):
        pass
    _blockPrint()
    for cluster, nets in X.items():
        if len(nets)==0:
            continue
        if len(nets[0])==0:
            continue
        for m,net in enumerate(nets[0]):
            if type == "DDI":
                genelist = [mapping[x.split("/")[0]] for x in list(net.nodes) if x.split("/")[0] in set(mapping.keys())]
            else:
                genelist = [mapping[x] for x in list(net.nodes) if x in set(mapping.keys())]
                
        
        
            gpro = GProfiler(return_dataframe=True)
            enrh = gpro.profile(organism=species,
                    query=genelist, no_evidences=False)
            
            mct = pvalue_correction(enrh['p_value'], method=p_adjust_method)
            enrh['adj_pval'] = mct.corrected_pvals
            enrh =enrh[enrh['adj_pval']<cutoff]
            enrh['cluster'] = f"Cluster {u}"
            enrh['module'] = f"Module {m}"

            enr = pd.concat([enrh])
            enr = enr.reset_index(drop=True)
            if term_source != "all":
                enr_results[cluster][u].append(enr[enr['source']=="all"])
            else:
                enr_results[cluster][u].append(enr)
            time.sleep(2)

            try:
                enr_results[cluster][m].append(enr.results[enr.results['Adjusted P-value']<cutoff])
            except:
                continue
            
        time.sleep(2)

    print("---------Gene Set Enrichment Result---------\n", file=sys.__stdout__)
    print(f"Method: {method} Database: {gene_sets}", file=sys.__stdout__)
    for u,v in enr_results.items():
        for m,vv in v.items():
            print("Cluster {} Module {}".format(u, m)," found enriched in {} terms.".format(vv[0].shape[0]), file=sys.__stdout__)
    print("-----END-----", file=sys.__stdout__)

    return enr_results

def list_genesets(organism):
    """
    Return a list of gene sets database

    Parameters
    -----------
    organism:
        human, mouse, etc.
    """
    return gp.get_library_name(organism)

